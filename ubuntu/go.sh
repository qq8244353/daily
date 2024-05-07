wget https://go.dev/dl/go1.22.2.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.22.2.linux-amd64.tar.gz
echo 'PATH=${PATH}:/usr/local/go/bin' >> ~/.zshrc
