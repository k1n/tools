import os
import time
import shutil

import changelog

from fabric.operations import local

def build(app, mode, version, distro):
    pass

def clean_and_prepare_build_root(app):
    src_dir = os.path.join(os.path.expanduser('~'), 'Sources', app)
    build_root = os.path.join(os.getcwd(), app)

    local('rm -rf ' + build_root)

    local('cp -r %s %s' % (src_dir, build_root))

    local('rm -rf ' + build_root + '/.git')
    local('rm -rf ' + build_root + '/.gitignore')
    local('rm -rf ' + build_root + '/.bzr')
    local('rm -rf ' + build_root + '/.bzrignore')
    local('rm -rf ' + build_root + '/build')
    local('find %s -name "*.pyc" | xargs rm -rf' % build_root)

def clean_and_prepare_tarball(app, version):
    src_dir = os.path.join(os.path.expanduser('~'), 'Sources', app)
    build_root = os.path.join(src_dir, 'dist')
    build_dir = os.path.join(build_dir, '%s-%s' % (app, version))
    tarball = os.path.join(build_root, '%s-%s.tar.gz' % (app, version))
    origball = os.path.join(build_root, '%s_%s.orig.tar.gz' % (app, version))
    changelog = os.path.join(build_dir, 'debian/changelog')

    local('rm -rf ' + build_root + '*')

    local('cd %s && python setup.py sdist' % src_dir)
    local('mv %s %s' % (tarball, origball))

    local('tar zxf %s -C $/' % (origball, build_root))
    local('cp -r %s/debian %s/debian' % (src_dir, build_dir))


def daily_build(app, version=None, *args, **kwargs):
    app = app.replace('-', '_')
    function_name = 'daily_build_%s' % app
    if function_name in globals():
        globals()[function_name](version=version, *args, **kwargs)

def daily_build_ubuntu_tweak_0(*args, **kwargs):
    daily_build_ubuntu_tweak(app='ubuntu-tweak-0', *args, **kwargs)

def daily_build_ubuntu_tweak(app='ubuntu-tweak', *args, **kwargs):
    version=None
    src_dir = os.path.join(os.path.expanduser('~'), 'Sources', app)
    build_root = os.path.join(os.getcwd(), app)
    pkg_name = ''.join(app.split('-'))
    version = local("cd %s && python -c 'import %s;print %s.__version__'" % (src_dir, pkg_name, pkg_name), capture=True)
    revno = 'bzr' + local("cd %s && bzr revno" % src_dir, capture=True)

    print("Start to build Ubuntu Tweak %s..." % version)
    clean_and_prepare_build_root(app)
    local("cd %s && echo \"__version__ = '.'.join(map(str, VERSION)) + '+%s'\" >> %s/__init__.py" % \
            (build_root, time.strftime('%Y%m%d', time.localtime()), pkg_name), capture=True)

    suffix = kwargs.pop('suffix', '1')
    mode = kwargs.pop('mode', 's')
    distros = kwargs.pop('distros', os.popen('lsb_release -cs').read().strip())

    for distro in distros.split('-'):
        changelog.make_daily(app, version, revno, distro,
                             os.path.join(build_root, 'debian/changelog'), suffix)
        if mode == 'b':
            local('cd %s && debuild' % build_root, capture=False)
        else:
            local('cd %s && debuild -S -sa' % build_root, capture=False)

def release_ubuntu_tweak(app='ubuntu-tweak', version=None, *args, **kwargs):
    src_dir = os.path.join(os.path.expanduser('~'), 'Sources', app)
    build_root = os.path.join(os.getcwd(), app)
    version =  local("cd %s && python -c 'import ubuntutweak;print ubuntutweak.__version__'" % src_dir, capture=True)

def daily_recipe():
    local('rm -rf working')
    local('bzr dailydeb ubuntu-tweak.recipe working --allow-fallback-to-native')
