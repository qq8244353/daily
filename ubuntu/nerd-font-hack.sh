TMP_DIR=$(mktemp -d)
cd ${TMP_DIR}
trap "rm -rf ${TMP_DIR}" EXIT

wget https://github.com/source-foundry/Hack/releases/download/v3.003/Hack-v3.003-ttf.zip
unzip Hack-v3.003-ttf.zip
FONT_DIR=/home/$(whoami)/.local/share/fonts
mkdir -p ${FONT_DIR}
cp -r ttf ${FONT_DIR}
