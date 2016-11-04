# This is an example PKGBUILD file. Use this as a start to creating your own,
# and remove these comments. For more information, see 'man PKGBUILD'.
# NOTE: Please fill out the license field for your package! If it is unknown,
# then please put 'unknown'.

# See http://wiki.archlinux.org/index.php/Python_Package_Guidelines for more
# information on Python packaging.

# Maintainer: Charles Schimmelpfennig <charlesschimmel@gmail.com>
pkgname=korminote
pkgver=0.7
pkgrel=1
pkgdesc="A full-featured Kodi remote with command or TUI interface"
arch=('any')
url="http://github.com/CharlesSchimmel/korminote"
license=('Creative Commons by-nc-sa')
groups=()
depends=('python' 'python-requests' 'python-pip' 'python-setuptools')
makedepends=('git' 'python-setuptools')
provides=('korminote')
conflicts=('korminote')
replaces=('korminote')
backup=()
options=(!emptydirs)
# install=
source=("git://github.com/CharlesSchimmel/korminote.git")
md5sums=('SKIP')

# build() {
#   cd "$srcdir"
# }

package() {
  cd "$srcdir/$pkgname"
  python setup.py install --root="$pkgname/" --optimize=1
  if ! [[ -e $HOME/.korminote ]]; then 
    mkdir $HOME/.korminote
  fi
  if ! [[ -e $HOME/.korminote/config.ini ]]; then
    cp $srcdir/$pkgname/$pkgname/config.ini $HOME/.korminote/
  fi
}

