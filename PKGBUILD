# This is an example PKGBUILD file. Use this as a start to creating your own,
# and remove these comments. For more information, see 'man PKGBUILD'.
# NOTE: Please fill out the license field for your package! If it is unknown,
# then please put 'unknown'.

# See http://wiki.archlinux.org/index.php/Python_Package_Guidelines for more
# information on Python packaging.

# Maintainer: Your Name <youremail@domain.com>
pkgname=korminote
pkgver=0.7
pkgrel=1
pkgdesc="A full-featured Kodi remote with command or TUI interface"
arch=('any')
url="http://github.com/CharlesSchimmel/korminote"
license=('Creative Commons by-nc-sa')
groups=()
depends=('python' 'python-requests' 'python-pip')
makedepends=('git' 'python-setuptools')
provides=('korminote')
conflicts=('korminote')
replaces=('korminote')
backup=()
options=(!emptydirs)
# install=
source=("git://github.com/charlesschimmel/korminote")
md5sums=('SKIP')

#build() {
#}

package() {
  cd "$srcdir/$pkgname"
  python3 setup.py install --root="$pkgdir/" --optimize=1
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}

