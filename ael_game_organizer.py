import os
import glob
import hashlib
import json
import time
import sys
import argparse
import xml.etree.ElementTree as ET

class RomIgnoredError(RuntimeError):
    pass

class Rom(object):
    def __init__(self, system_dir, rom_name):
        rom_base_name = os.path.splitext(rom_name)[0]
        rom_dir = os.path.join(system_dir, 'roms/')
        boxart_dir = os.path.join(system_dir, 'media/box2dfront/')
        fanart_dir = os.path.join(system_dir, 'media/fanart/')
        json_dir = os.path.join(system_dir, 'media/json/')
        json_path = os.path.join(json_dir, rom_base_name + '.json')

        try:
            with open(json_path, 'r') as fd:
                rom_info = json.load(fd)
        except FileNotFoundError:
            print('ROM nfo invalid: {}'.format(json_path), file=sys.stderr)
            raise RomIgnoredError()
        except json.decoder.JSONDecodeError:
            print('ROM nfo invalid: {}'.format(json_path), file=sys.stderr)
            sys.exit(-1)

        self.id = hashlib.md5(rom_base_name.encode('utf8')).hexdigest()
        if rom_info['name']:
            self.name = rom_info['name']
        else:
            self.name = rom_base_name
        self.desc = rom_info['desc']
        self.rom_path = os.path.join(rom_dir, rom_name)
        self.boxart_path = _get_img_path(boxart_dir, rom_base_name)
        self.fanart_path = _get_img_path(fanart_dir, rom_base_name)
        try:
            self.add_to_lib = rom_info['add_to_lib']
        except KeyError:
            self.add_to_lib = True

        if not self.add_to_lib:
            raise RomIgnoredError()

    def __str__(self):
        return '{}'.format(self.name)

    def __repr__(self):
        return '{}'.format(self.name)

class System(object):
    def __init__(self, system_path):
        with open(os.path.join(system_path, 'platform.json'), 'r') as fd:
            platform = json.load(fd)

        self.path = system_path
        self.id = hashlib.md5(platform['name'].encode('utf8')).hexdigest()
        self.name = platform['name']
        self.plot = platform['desc']
        self.application = platform['application']
        self.args = platform['args']
        self.romext = platform['romext']
        self.poster = _get_img_path(system_path, 'platform_poster')
        self.icon = _get_img_path(system_path, 'platform_icon')
        self.fanart = _get_img_path(system_path, 'platform_fanart')
        self.rompath = roms_dir = os.path.join(self.path, 'roms/')
        self.roms = self._find_roms()

    def _find_roms(self):
        roms_dir = os.path.join(self.path, 'roms/')

        roms = []
        for rom_name in os.listdir(roms_dir):
            rom_path = os.path.join(roms_dir, rom_name)
            rom_is_file = os.path.isfile(rom_path)
            rom_ext = os.path.splitext(rom_path)[1].replace('.', '')
            if rom_is_file and rom_ext in self.romext:
                try:
                    roms.append(Rom(self.path, rom_name))
                except RomIgnoredError:
                    pass
        return roms

    def get_cat_name(self):
        return 'roms_root_category_{}_{}'.format(self.name.replace(' ', '_'), self.id[:6])

    def __str__(self):
        return '{} ({} Roms)'.format(self.name, len(self.roms))

    def __repr__(self):
        return '{} ({} Roms)'.format(self.name, len(self.roms))

def _get_img_path(dir_path, base_name):
    img_ext = ['.png', '.jpg', '.jpeg']

    img_path = None
    for ext in img_ext:
        tmp_path = os.path.join(dir_path, base_name + ext)
        if os.path.exists(tmp_path):
            img_path = tmp_path
            break

    return img_path

def output_launcher(systems, output_path):
    root = ET.Element('advanced_emulator_launcher', version='1')

    for system in systems:
        launcher = ET.SubElement(root, 'launcher')
        ET.SubElement(launcher, 'id').text = system.id
        ET.SubElement(launcher, 'm_name').text = system.name
        ET.SubElement(launcher, 'm_year').text = ''
        ET.SubElement(launcher, 'm_genre').text = ''
        ET.SubElement(launcher, 'm_developer').text = ''
        ET.SubElement(launcher, 'm_rating').text = ''
        ET.SubElement(launcher, 'm_plot').text = system.plot
        ET.SubElement(launcher, 'platform').text = system.name
        ET.SubElement(launcher, 'categoryID').text = 'root_category'
        ET.SubElement(launcher, 'application').text = system.application
        ET.SubElement(launcher, 'args').text = system.args
        ET.SubElement(launcher, 'rompath').text = system.rompath
        ET.SubElement(launcher, 'romext').text = '|'.join(system.romext)
        ET.SubElement(launcher, 'finished').text = 'False'
        ET.SubElement(launcher, 'minimize').text = 'False'
        ET.SubElement(launcher, 'non_blocking').text = 'False'
        ET.SubElement(launcher, 'roms_base_noext').text = system.get_cat_name()
        ET.SubElement(launcher, 'nointro_xml_file').text = ''
        ET.SubElement(launcher, 'nointro_display_mode').text = 'All ROMs'
        ET.SubElement(launcher, 'launcher_display_mode').text = 'Flat mode'
        ET.SubElement(launcher, 'num_roms').text = str(len(system.roms))
        ET.SubElement(launcher, 'num_parents').text = '0'
        ET.SubElement(launcher, 'num_clones').text = '0'
        ET.SubElement(launcher, 'num_have').text = '0'
        ET.SubElement(launcher, 'num_miss').text = '0'
        ET.SubElement(launcher, 'num_unknown').text = '0'
        ET.SubElement(launcher, 'timestamp_lancher').text = str(time.time())
        ET.SubElement(launcher, 'timestamp_report').text = '0.0'
        ET.SubElement(launcher, 'default_icon').text = 's_icon'
        ET.SubElement(launcher, 'default_fanart').text = 's_fanart'
        ET.SubElement(launcher, 'default_banner').text = 's_banner'
        ET.SubElement(launcher, 'default_poster').text = 's_poster'
        ET.SubElement(launcher, 'default_clearlogo').text = 's_clearlogo'
        ET.SubElement(launcher, 'default_controller').text = 's_controller'
        ET.SubElement(launcher, 'Asset_Prefix').text = ''
        ET.SubElement(launcher, 's_icon').text = system.icon
        ET.SubElement(launcher, 's_fanart').text = system.fanart
        ET.SubElement(launcher, 's_banner').text = ''
        ET.SubElement(launcher, 's_poster').text = system.poster
        ET.SubElement(launcher, 's_clearlogo').text = ''
        ET.SubElement(launcher, 's_controller').text = ''
        ET.SubElement(launcher, 's_trailer').text = ''
        ET.SubElement(launcher, 'roms_default_icon').text = 's_boxfront'
        ET.SubElement(launcher, 'roms_default_fanart').text = 's_fanart'
        ET.SubElement(launcher, 'roms_default_banner').text = 's_banner'
        ET.SubElement(launcher, 'roms_default_poster').text = 's_flyer'
        ET.SubElement(launcher, 'roms_default_clearlogo').text = 's_clearlogo'
        ET.SubElement(launcher, 'ROM_asset_path').text = ''
        ET.SubElement(launcher, 'path_title').text = ''
        ET.SubElement(launcher, 'path_snap').text = ''
        ET.SubElement(launcher, 'path_boxfront').text = ''
        ET.SubElement(launcher, 'path_boxback').text = ''
        ET.SubElement(launcher, 'path_cartridge').text = ''
        ET.SubElement(launcher, 'path_fanart').text = ''
        ET.SubElement(launcher, 'path_banner').text = ''
        ET.SubElement(launcher, 'path_clearlogo').text = ''
        ET.SubElement(launcher, 'path_flyer').text = ''
        ET.SubElement(launcher, 'path_map').text = ''
        ET.SubElement(launcher, 'path_manual').text = ''
        ET.SubElement(launcher, 'path_trailer').text = ''

    tree = ET.ElementTree(root)
    tree.write(os.path.join(output_path, 'categories.xml'), xml_declaration=True, encoding='utf-8')

def output_roms(system, output_path):
    rom_output = {}
    for rom in system.roms:
        rom_temp = {}
        rom_temp['altapp'] = ''
        rom_temp['altarg'] = ''
        rom_temp['cloneof'] = ''
        rom_temp['disks'] = [] # TODO
        rom_temp['filename'] = rom.rom_path
        rom_temp['finished'] = False
        rom_temp['id'] = rom.id
        rom_temp['m_developer'] = ''
        rom_temp['m_esrb'] = ''
        rom_temp['m_genre'] = ''
        rom_temp['m_name'] = rom.name
        rom_temp['m_nplayers'] = ''
        rom_temp['m_plot'] = rom.desc
        rom_temp['m_rating'] = ''
        rom_temp['m_year'] = ''
        rom_temp['nointro_status'] = 'None'
        rom_temp['pclone_status'] = 'None'
        rom_temp['s_banner'] = ''
        rom_temp['s_boxback'] = ''
        rom_temp['s_boxfront'] = rom.boxart_path
        rom_temp['s_cartridge'] = ''
        rom_temp['s_clearlogo'] = ''
        rom_temp['s_fanart'] = rom.fanart_path
        rom_temp['s_flyer'] = ''
        rom_temp['s_manual'] = ''
        rom_temp['s_map'] = ''
        rom_temp['s_snap'] = ''
        rom_temp['s_title'] = ''
        rom_temp['s_trailer'] = ''
        rom_output[rom.id] = rom_temp

    roms_dir = os.path.join(output_path, 'db_ROMs')
    try:
        os.mkdir(roms_dir)
    except FileExistsError:
        pass

    output_file = system.get_cat_name() + '.json'
    output_path = os.path.join(roms_dir, output_file)
    with open(output_path, 'w') as fd:
        json.dump(rom_output, fd, indent=1)

def check_system(system, verbose):
    err_msg = ''

    if not system.name:
        err_msg += '  Platform name missing\n'
    if not system.plot:
        err_msg += '  Platform plot missing\n'
    if not system.application:
        err_msg += '  Platform application missing\n'
    if not system.args:
        err_msg += '  Platform args missing\n'
    if not system.poster:
        err_msg += '  Platform poster missing\n'
    if not system.icon:
        err_msg += '  Platform icon missing\n'
    if not system.fanart:
        err_msg += '  Platform fanart missing\n'

    for rom in system.roms:
        rom_err_msg = ''

        if not rom.name:
            rom_err_msg += '      Rom name missing\n'
        if not rom.desc:
            rom_err_msg += '      Rom desc missing\n'
        if not rom.boxart_path:
            rom_err_msg += '      Rom boxart_path missing\n'
        if not rom.fanart_path:
            rom_err_msg += '      Rom fanart_path missing\n'

        if rom_err_msg or verbose:
            err_msg += '  - {}\n'.format(rom)
            err_msg += rom_err_msg

    if err_msg or verbose:
        print('{}'.format(system))
        print(err_msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    systems = []
    for dir in os.listdir(args.input):
        try:
            system = System(os.path.join(args.input, dir))
        except FileNotFoundError as e:
            print('System {} skipped'.format(dir))
            continue
        systems.append(system)

    output_launcher(systems, args.output)
    for system in systems:
        if args.check or args.verbose:
            check_system(system, args.verbose)
        output_roms(system, args.output)
