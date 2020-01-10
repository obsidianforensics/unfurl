![Unfurl Logo](/static/unfurl.png)

# Extract and Visualize Data from URLs using Unfurl
Unfurl takes a URL and expands ("unfurls") it into a directed graph, extracting every bit of information from the URL and 
exposing the obscured. It does this by breaking up a URL into components, extracting as much information as it can from 
each piece, and presenting it all visually. This “show your work” approach (along with embedded references and documentation) 
makes the analysis transparent to the user and helps them learn about (and discover) semantic and syntactical URL structures.

Unfurl has parsers for URLs, search engines, chat applications, social media sites, and more. It also has more generic parsers 
(timestamps, UUIDs, etc) helpful for exploring new URLs or reverse engineering. It’s also easy to build new parsers, since 
Unfurl is open source (Python 3) and has an extensible plugin system.

No matter if you extracted a URL from a memory image, carved it from slack space, or pulled it from a browser’s history file, 
Unfurl can help you get the most out of it. 

## How to use Unfurl

### Online Version

1. There is an online version at **https://dfir.blog/unfurl**. Visit that page, enter the URL in the form, and 
click 'Unfurl!'. 
2. You can also access the online version using a bookmarklet - create a new bookmark and paste 
`javascript:window.location.href='https://dfir.blog/unfurl/?url='+window.location.href;` as the location. Then when on any
page with an interesting URL, you can click the bookmarklet and see the URL "unfurled".

### Local Install

1. Clone or download Unfurl from GitHub.
1. Install Python 3 and the modules in `requirements.txt`
1. Run `python unfurl_app.py`
1. Browse to 127.0.0.1:5000/
1. Enter the URL to unfurl in the form, and 'Unfurl!'

## Legal Bit
This is not an officially supported Google product.
