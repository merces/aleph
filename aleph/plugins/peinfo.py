from aleph.base import PluginBase
import pefile, sys, traceback, bitstring, string, hashlib, bz2
import datetime, time

class PEInfoPlugin(PluginBase):
    """Analyze PE binary files"""
    name = 'pe_info'
    default_options = { 'enabled': True }
    mimetypes = ['application/x-dosexec']

    def process(self):
        """Analyze PE binary files"""

        try:
            return self.get_pe_data()
                            
        except Exception, e:
            print sys.exc_info()[0]
            print traceback.format_exc()
            self.logger.error('Cannot parse sample %s. Not PE?' % self.sample.uuid)
            raise

    def get_pe_data(self):
        """Get Portable Executable (PE) files data

        Return example:

        {   'aslr': True,
            'dep': True,
            'seh': True,
            'architechture': '32-bit',
            'compilation_date': '2009-12-05 22:50:46',
            'compilation_timestamp': 1260053446,
            'number_sections': 5,
            'exports': [{'ordinal': 1, 'name': 'DriverProc', 'address': '0x1c202070'}, { ... } ],
            'imports': { 'LIB': [ { 'address': '0x407000', 'name': 'function'}, ... ], ... },
            'sections': [ { 'address': '0x1000', 'name': '.text','raw_size': 23552,'virtual_size': '0x5a5a'}, {  ... } ]
        }

        """
        pe = pefile.PE(self.sample.path, fast_load=True)

        pe.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_TLS'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])
        data = {}
        # Get Architechture
        if pe.FILE_HEADER.Machine == 0x14C:  # IMAGE_FILE_MACHINE_I386
            data['architechture'] = '32-bit'
            # data['pehash'] = self. pehash() # Temporarily disabled due problems
            self.sample.add_tag('i386')
        elif pe.FILE_HEADER.Machine == 0x8664:  # IMAGE_FILE_MACHINE_AMD64
            data['architechture'] = '64-bit'
            self.sample.add_tag('amd64')
        else:
            data['architechture'] = 'N/A'

        # Executable Type
        self.sample.add_tag('dll' if pe.is_dll() else 'exe')
        if pe.is_driver():
            self.sample.add_tag('driver')

        # Compilation time
        timestamp = pe.FILE_HEADER.TimeDateStamp
        if timestamp == 0:
            self.sample.add_tag('no-timestamp')
        else:
            data['compilation_timestamp'] = timestamp
            data['compilation_date'] = datetime.datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            if (timestamp < 946692000):
                self.sample.add_tag('old-timestamp')
            elif (timestamp > time.time()):
                self.sample.add_tag('future-timestamp')

        # data['entry_point'] = pe.OPTIONAL_HEADER.AddressOfEntryPoint
        #data['image_base']  = pe.OPTIONAL_HEADER.ImageBase
        data['number_sections'] = pe.FILE_HEADER.NumberOfSections
        #check for ASLR, DEP/NX and SEH
        if pe.OPTIONAL_HEADER.DllCharacteristics > 0:
            if pe.OPTIONAL_HEADER.DllCharacteristics & 0x0040:
                data['aslr'] = True
            if pe.OPTIONAL_HEADER.DllCharacteristics & 0x0100:
                data['dep'] = True
            if (pe.OPTIONAL_HEADER.DllCharacteristics & 0x0400
                or (hasattr(pe, "DIRECTORY_ENTRY_LOAD_CONFIG")
                    and pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.SEHandlerCount > 0
                    and pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.SEHandlerTable != 0)
                or pe.FILE_HEADER.Machine == 0x8664):
                data['seh'] = True

        # Check imports
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            imports = {}
            for lib in pe.DIRECTORY_ENTRY_IMPORT:
                imports[lib.dll] = []
                for imp in lib.imports:
                    if (imp.name != None) and (imp.name != ""):
                        imports[lib.dll].append({'address': hex(imp.address), 'name': imp.name})

            data['imports'] = imports

        # Check exports
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            exports = []
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                exports.append({'address': hex(pe.OPTIONAL_HEADER.ImageBase + exp.address), 'name': exp.name,
                                'ordinal': exp.ordinal})
                if exp.name == 'CPlApplet' and pe.is_dll():
                    self.sample.add_tag('cpl')

            data['exports'] = exports

        # Get sections
        if len(pe.sections) > 0:
            data['sections'] = []
            for section in pe.sections:
                data['sections'].append(
                    {'name': section.Name.replace('\x00', ''), 'address': hex(section.VirtualAddress),
                     'virtual_size': hex(section.Misc_VirtualSize), 'raw_size': section.SizeOfRawData})

        return data

    def pehash(self):
        """ Create a hash from the sample
            You can read more at https://www.usenix.org/legacy/event/leet09/tech/full_papers/wicherski/wicherski_html/"""
        pe = pefile.PE(self.sample.path, fast_load=True)
        img_chars = bitstring.BitArray(hex(pe.FILE_HEADER.Characteristics))
        img_chars = bitstring.BitArray(bytes = img_chars.tobytes())
        img_chars_xor = img_chars[0:8] ^ img_chars[8:16]
        pehash_bin = bitstring.BitArray(img_chars_xor)
        sub_chars = bitstring.BitArray(hex(pe.FILE_HEADER.Machine))
        sub_chars = bitstring.BitArray(bytes = sub_chars.tobytes())
        sub_chars_xor = sub_chars[0:8] ^ sub_chars[8:16]
        pehash_bin.append(sub_chars_xor)
        stk_size = bitstring.BitArray(hex(pe.OPTIONAL_HEADER.SizeOfStackCommit))
        stk_size_bits = string.zfill(stk_size.bin, 32)
        stk_size = bitstring.BitArray(bin=stk_size_bits)
        stk_size_xor = stk_size[8:16] ^ stk_size[16:24] ^ stk_size[24:32]
        stk_size_xor = bitstring.BitArray(bytes=stk_size_xor.tobytes())
        pehash_bin.append(stk_size_xor)
        hp_size = bitstring.BitArray(hex(pe.OPTIONAL_HEADER.SizeOfHeapCommit))
        hp_size_bits = string.zfill(hp_size.bin, 32)
        hp_size = bitstring.BitArray(bin=hp_size_bits)
        hp_size_xor = hp_size[8:16] ^ hp_size[16:24] ^ hp_size[24:32]
        hp_size_xor = bitstring.BitArray(bytes=hp_size_xor.tobytes())
        pehash_bin.append(hp_size_xor)

        for section in pe.sections:
            sect_va =  bitstring.BitArray(hex(section.VirtualAddress))
            sect_va = bitstring.BitArray(bytes=sect_va.tobytes())
            sect_va_bits = sect_va[8:32]
            pehash_bin.append(sect_va_bits)
            sect_rs =  bitstring.BitArray(hex(section.SizeOfRawData))
            sect_rs = bitstring.BitArray(bytes=sect_rs.tobytes())
            sect_rs_bits = string.zfill(sect_rs.bin, 32)
            sect_rs = bitstring.BitArray(bin=sect_rs_bits)
            sect_rs = bitstring.BitArray(bytes=sect_rs.tobytes())
            sect_rs_bits = sect_rs[8:32]
            pehash_bin.append(sect_rs_bits)
            sect_chars =  bitstring.BitArray(hex(section.Characteristics))
            sect_chars = bitstring.BitArray(bytes=sect_chars.tobytes())
            sect_chars_xor = sect_chars[16:24] ^ sect_chars[24:32]
            pehash_bin.append(sect_chars_xor)
            address = section.VirtualAddress
            size = section.SizeOfRawData
            raw = pe.write()[address+size:]
            if size == 0: 
                kolmog = bitstring.BitArray(float=1, length=32)
                pehash_bin.append(kolmog[0:8])
                continue
            bz2_raw = bz2.compress(raw)
            bz2_size = len(bz2_raw)
            #k = round(bz2_size / size, 5)
            k = bz2_size / size
            kolmog = bitstring.BitArray(float=k, length=32)
            pehash_bin.append(kolmog[0:8])
        m = hashlib.sha1()
        m.update(pehash_bin.tobytes())
        return m.hexdigest()

def setup(queue):
    plugin = PEInfoPlugin(queue)
    return plugin