set -euo pipefail
[[ "${TRACE-0}" == "1" ]] && set -x

for s in $HOME/rpmbuild/SPECS/*.spec
do
  rpmlint $s
  rpmbuild -ba $s
done
