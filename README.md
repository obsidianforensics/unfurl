<picture>
  <source srcset="/unfurl/static/unfurl_dark.png" media="(prefers-color-scheme: dark)">
  <img src="/unfurl/static/unfurl.png" alt="Unfurl Logo">
</picture>

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

<img src="docs/unfurl-demo.gif"/>

## How to use Unfurl

### Online Version

1. There is an online version at **https://dfir.blog/unfurl**. Visit that page, enter the URL in the form, and 
click 'Unfurl!'. 
2. You can also access the online version using a bookmarklet - create a new bookmark and paste 
`javascript:window.location.href='https://dfir.blog/unfurl/?url='+window.location.href;` as the location. Then when on any
page with an interesting URL, you can click the bookmarklet and see the URL "unfurled".

### Local Python Install

1. Install via pip: `pip install dfir-unfurl`

After Unfurl is installed, you can run use it via the web app or command-line:

1. Run `python unfurl_app.py`
1. Browse to localhost:5000/ (editable via config file)
1. Enter the URL to unfurl in the form, and 'Unfurl!'

OR

1. Run `python unfurl_cli.py https://twitter.com/_RyanBenson/status/1205161015177961473`
1. Output: 
```
[1] https://twitter.com/_RyanBenson/status/1205161015177961473
 ├─(u)─[2] Scheme: https
 ├─(u)─[3] twitter.com
 |  ├─(u)─[5] Domain Name: twitter.com
 |  └─(u)─[6] TLD: com
 └─(u)─[4] /_RyanBenson/status/1205161015177961473
    ├─(u)─[7] 1: _RyanBenson
    ├─(u)─[8] 2: status
    └─(u)─[9] 3: 1205161015177961473
       ├─(❄)─[10] Timestamp: 1576167751484
       |  └─(🕓)─[13] 2019-12-12 16:22:31.484
       ├─(❄)─[11] Machine ID: 334
       └─(❄)─[12] Sequence: 1 
```

If the URL has special characters (like "&") that your shell might interpret as a command, put the URL in quotes. 
Example: `python unfurl_cli.py "https://www.google.com/search?&ei=yTLGXeyKN_2y0PEP2smVuAg&q=dfir.blog&oq=dfir.blog&ved=0ahUKEwisk-WjmNzlAhV9GTQIHdpkBYcQ4dUDCAg"`

`unfurl_cli` has a number of command line options to modify its behavior:
```
optional arguments:
  -h, --help            show this help message and exit
  -d, --detailed        show more detailed explanations.
  -f FILTER, --filter FILTER
                        only output lines that match this filter.
  -o OUTPUT, --output OUTPUT
                        file to save output (as CSV) to. if omitted, output is sent to stdout (typically this means displayed in the console).
  -v, -V, --version     show program's version number and exit
```

### Docker 

1. `git clone https://github.com/obsidianforensics/unfurl`
1. `cd unfurl`
1. `docker-compose up -d`

## Testing 

1. All tests are run automatically on each PR by Travis CI. Tests need to pass before merging. 
1. While not required, it is strongly encouraged to add tests that cover any new features in a PR. 
1. To manually run all tests (units and integration): ``python -m unittest discover -s unfurl/tests``

If using Docker as above, run: 
``docker exec unfurl python -m unittest discover -s unfurl/tests``

## Legal Bit
This is not an officially supported Google product.
