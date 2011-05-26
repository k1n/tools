import os
import shutil

import changelog

from fabric.operations import local

def build(app, mode, version, distro):
    pass

def clean_and_prepare_build_root(app):
    src_dir = os.path.join(os.path.expanduser('~'), 'Sources', app)
    build_root = os.path.join(os.getcwd(), app)

    local('rm -rf ' + build_root + '*')

    local('cp -r %s %s' % (src_dir, build_root))

    local('rm -rf ' + build_root + '/.git')
    local('rm -rf ' + build_root + '/.gitignore')
    local('rm -rf ' + build_root + '/build')
    local('find %s -name "*.pyc" | xargs rm -rf' % build_root)

def daily_build(app, version=None, *args, **kwargs):
    app = app.replace('-', '_')
    function_name = 'daily_build_%s' % app
    if function_name in globals():
        globals()[function_name](version=version, *args, **kwargs)

def daily_build_ubuntu_tweak(app='ubuntu-tweak', version=None, *args, **kwargs):
    src_dir = os.path.join(os.path.expanduser('~'), 'Sources', app)
    build_root = os.path.join(os.getcwd(), app)
    version =  local("cd %s && python -c 'import ubuntutweak;print ubuntutweak.__version__'" % src_dir, capture=True)

    print("Start to build Ubuntu Tweak %s..." % version)
    clean_and_prepare_build_root(app)

    suffix = kwargs.pop('suffix', '1')
    mode = kwargs.pop('mode', 's')
    changelog.make_daily(app, version, 'natty', os.path.join(build_root, 'debian/changelog'), suffix)
    if mode == 'b':
        local('cd %s && debuild' % build_root, capture=False)
    else:
        local('cd %s && debuild -S -sa' % build_root, capture=False)
