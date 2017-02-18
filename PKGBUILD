# Maintainer: Charles Schimmelpfennig <charlesschimmel@gmail.com>
pkgname=korminote
pkgver=0.72
pkgrel=1
pkgdesc="A full-featured Kodi remote with command or TUI interface"
arch=('any')
url="http://github.com/CharlesSchimmel/korminote"
license=('MIT')
depends=('python' 'python-requests' 'python-pip' 'python-setuptools')
makedepends=('git' 'python-setuptools')
provides=('korminote')
conflicts=('korminote')
replaces=('korminote')
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

