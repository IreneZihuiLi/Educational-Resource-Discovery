# Google Chrome Browser
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd6
4.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb; sudo apt-get -f install
rm google-chrome-stable_current_amd64.deb

# Chrome Webdriver for Linux
wget https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
rm chromedriver_linux64.zip

# Python Packages
pip3 install bs4
pip3 install pandas
pip3 install ordered-set
pip3 install selenium
