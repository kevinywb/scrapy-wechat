from html.parser import HTMLParser


class Html2Markdown(HTMLParser):
    # output markdown text
    __output = ''

    # take a unique placeholder then replace text
    __placeholder = '3f4ec2b893ce4f1ab0f4c0861ef9dae7'

    # mark content between start tag and end tag
    __content = ''

    # mark hidden between start tag and end tag
    __hidden = False

    # mark new line between start tag and end tag
    __newline = True

    # mark prefix line between start tag and end tag
    __prefix = False

    # set no space mode
    __no_space = True

    # define replacemen rules - 0: starttag, 1: endtag
    __rule_replacement = {
        'a': ('', ''),
        'blockquote': ('\n', '\n'),
        'code': (' ``` ', ' ``` '),
        'div': ('', '\n'),
        # 'em': (' *', '* '),
        'h1': ('# ', '\n'),
        'h2': ('## ', '\n'),
        'h3': ('### ', '\n'),
        'h4': ('#### ', '\n'),
        'h5': ('##### ', '\n'),
        'h6': ('###### ', '\n'),
        'hr': ('', ' ----- \n'),
        'img': ('', '\n\n'),
        'p': ('', '\n'),
        'pre': ('', '\n'),
        'strong': (' **', '** '),
        'ul': ('\n', '\n')
    }

    @property
    def output(self):
        r = self.__output
        r = r.replace('  ', '')
        r = r.replace('\n\n\n', '\n')
        r = r.replace('****', '')
        r = r.replace('```  ```', '')
        return r.strip()

    # default parse
    def default_parse(self, tag, alone):
        if alone is True:
            i = 0
        else:
            i = 1
        if tag in self.__rule_replacement:
            it = self.__rule_replacement[tag]
            self.__output += it[i]

    # handle start tag
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, val) in attrs:
                if key == 'href':
                    self.__content = f'[{self.__placeholder}]({val})'

        if tag == 'blockquote':
            self.__prefix = True

        if tag == 'code':
            self.__content = self.__placeholder
            self.__no_space = False

        if tag == 'figcaption':
            self.__hidden = True

        if tag == 'li':
            if self.__prefix is True:
                self.__output += '>'
            else:
                self.__output += '* '
            self.__newline = False

        if tag == 'p':
            if self.__newline is True:
                self.__output += '\n'

        if tag == 'pre':
            self.__rule_replacement['code'] = (' ``` \n', ' \n ``` ')

        # default parse
        self.default_parse(tag, True)

    # handle text data
    def handle_data(self, data):
        data = data.replace('\xa0', '')
        if len(self.__content) > 0:
            self.__output += self.__content.replace(self.__placeholder, data)
            self.__content = ''
        elif self.__hidden is False:
            self.__output += data

    # handle end tag
    def handle_endtag(self, tag):
        if tag == 'blockquote':
            self.__output += '\n'
            self.__prefix = False

        if tag == 'code':
            self.__no_space = True

        if tag == 'figcaption':
            self.__hidden = False

        if tag == 'li':
            self.__newline = True

        if tag == 'pre':
            self.__rule_replacement['code'] = (' ``` ', ' ``` ')

        # default parse
        self.default_parse(tag, False)

    # handle never end tag
    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            if self.__newline is True:
                self.__output += '\n'

        if tag == 'img':
            for (key, val) in attrs:
                if key == 'data-src':
                    self.__output += f'![]({val}&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)'

        # default parse
        self.default_parse(tag, False)
