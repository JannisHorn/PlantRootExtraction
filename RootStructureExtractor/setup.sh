# RootStructureExtractor/setup.sh
# Calls setup for c_graph_interface
# Combines possible calls for c-compilation

cdScriptDir()
{
  SCRIPT="$(readlink -f "$0")"
  SCRIPTPATH="$(dirname "$0")"
  cd "${SCRIPTPATH}"
  echo "$PWD"
}


findCGraphInterface()
{
  SETUP_FILE_PATH="./PyUtils/c_graph_interface/"
  SETUP_FILE="setup.py"
  SETUP_RUNNER="${SETUP_FILE_PATH}${SETUP_FILE}"
  if [ -f "${SETUP_RUNNER}" ]; then
    echo "Found setup file: $SETUP_RUNNER"
  else
    echo "Error: in $SCRIPTPATH/setup.sh"
    echo "    Could not locate: $SETUP_RUNNER"
    echo "    Terminating Setup: Exit Code 1"
    exit 1
  fi
}


setupCGraphInterface()
{
  findCGraphInterface
  ( cd ${SETUP_FILE_PATH} && python ${SETUP_FILE} clean --all && python ${SETUP_FILE} build )
}


rflag=0
cflag=1
pyflag=0
eflag=0
debflag=0

for arg in "$@"
do
  case "$arg" in
  -r*) rflag=1 ;;
  -c*) cflag=1 ;;
  -p*) pyflag=1 ;;
  --full*) rflag=1
           cflag=1
           pyflag=1 ;;
  --debug*) cflag=1
            rflag=1
            debflag=1 ;;
  --eval*) cflag=1
           eflag=1 ;;
  esac
done

(
#set -x
cmakeflags=""
cd "$(dirname "$0")"
if [ "$debflag" == 1 ]; then
  cmakeflags="$cmakeflags -DCMAKE_BUILD_TYPE=RelWithDebInfo"
  cflag=1
else
  cmakeflags="$cmakeflags -DCMAKE_BUILD_TYPE=Release"
fi
if [ "$eflag" == 1 ]; then
  cmakeflags="$cmakeflags -DCOMP_EVAL=ON"
else
  cmakeflags="$cmakeflags -DCOMP_EVAL=OFF"
fi
if [ "$cflag" == 1 ]; then
  echo "cmakeflags $cmakeflags"
  rm -r ./build
  mkdir build
  cd ./build
  cmake $cmakeflags ..
  #cmake --build . --clean-first
  cd ..
fi
if [ "$rflag" == 1 ]; then
  cd build
  make clean
  cd ..
fi
cd build
make -j2
cd ..
if [ "$pyflag" == 1 ]; then
  cdScriptDir
  setupCGraphInterface
fi
)
