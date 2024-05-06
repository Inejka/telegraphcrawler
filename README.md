# Telegraphcrawler
## About
Telegraphcrawler is a tool to index [telegra.ph](https://telegra.ph/) pages based on the provided wordslist. Inspired by [nudecrawler](https://github.com/yaroslaff/nudecrawler), this project uses multithreading alongside with multiprocessing, but doesn't feature any tools to filter discovered content for now. Html pages, links to images and videos are saved into postgreSQL database for future analyzing.
## Usage
- Create folder to work in:
```
mkdir telegraphcrawler
cd telegraphcrawler
```
- Download docker-compose and .env_example files:
```
curl -LO https://raw.githubusercontent.com/Inejka/telegraphcrawler/master/docker-compose.yml
curl -LO https://raw.githubusercontent.com/Inejka/telegraphcrawler/master/.env_example
```
- Rename .env_example to .env and change default values if needed (at least default password):
```
mv ./.env_example ./.env
```
- Create work folder and dict folder, fill your first wordlist:
```
mkdir work
mkdir work/dict
echo -e "cat\nkitty\ndog\nduck\nrabbit\nchicken\nguinea-pig\ndonkey\npigeon\ngoose\nllama\nalpaca\ngoldfish\nparrot" > work/dict/first.txt 
```
- Run with docker-compose and enter TUI:
```
docker-compose run --rm crawler 
```
- Stop db after work:
```
docker-compose stop  
```
