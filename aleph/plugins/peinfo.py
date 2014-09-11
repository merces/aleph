from aleph.base import PluginBase
import pefile, sys, traceback

class PEInfoPlugin(PluginBase):

    name = 'pe_info'
    mimetypes = ['application/x-dosexec']
    default_options = { 'enabled': True }

    def process(self):

        try:
            pe = pefile.PE(self.sample.path, fast_load=True)
            pe.parse_data_directories( directories=[ 
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_TLS'],
                pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])

            data = {}

            # Get sections
            if len(pe.sections) > 0:
                data['sections'] = []
                for section in pe.sections:
                    data['sections'].append({'name': section.Name.replace('\x00', ''), 'address': hex(section.VirtualAddress), 'virtual_size': hex(section.Misc_VirtualSize), 'raw_size': section.SizeOfRawData })

            # Get Architechture
            if pe.FILE_HEADER.Machine == 0x14C: # IMAGE_FILE_MACHINE_I386
                data['arch'] = '32 bits'
                self.sample.add_tag('32-bit')
            elif pe.FILE_HEADER.Machine == 0x8664: # IMAGE_FILE_MACHINE_AMD64
                data['arch'] = '64 bits'
                self.sample.add_tag('64-bit')


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
                    exports.append({'address': hex(pe.OPTIONAL_HEADER.ImageBase + exp.address), 'name': exp.name, 'ordinal': exp.ordinal})

                data['exports'] = exports

            data['entry_point'] = pe.OPTIONAL_HEADER.AddressOfEntryPoint
            data['image_base']  = pe.OPTIONAL_HEADER.ImageBase
            data['number_sections'] = pe.FILE_HEADER.NumberOfSections

            # Add general tags
            self.sample.add_tag('windows')
            self.sample.add_tag('pe')

            return data
                            
        except Exception, e:
            print sys.exc_info()[0]
            print traceback.format_exc()
            self.logger.error('Cannot parse sample %s. Not PE?' % self.sample.uuid)
            raise

def setup(queue):
    plugin = PEInfoPlugin(queue)
    return plugin
