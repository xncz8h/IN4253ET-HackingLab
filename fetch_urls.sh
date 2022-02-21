wget -qO- https://www.overheid.nl/english/dutch-government-websites |
grep -Eoi '<a [^>]+>' | 
grep -Eo 'href="[^\"]+"' | 
grep -Eo '(http|https)://[^/"]+' |
sort -u |
sed 's/https:\/\///g' |
sed 's/http:\/\///g' |
sed 's/www.//g' > out.txt
