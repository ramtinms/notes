import re


class SimpleMarkdownParser():

    def __init__(self):
        self._main_header_pattern = re.compile("^#\W([\w \.\,\!\;\:\-\_\'\\\"]+)")
        self._subheader_pattern = re.compile("^##+\W|##+\W")
        self._linebreak_pattern = re.compile("\n==+\n|^==+\n|\n--+\n|^--+\n")
        self._strong_emphasis_pattern = re.compile("\*{2}|\_{2}([\w \.\,\!\;\:\-\'\\\"]+)\*{2}|\_{2}")
        self._emphasis_pattern = re.compile("\*|\_([\w \.\,\!\;\:\-\'\\\"]+)\*|\_")
        self._inline_pattern = re.compile("\`([\w \.\,\!\;\:\-\'\\\"]+)\`")
        self._strikethrough_pattern = re.compile("\~\~([\w \.\,\!\;\:\-\'\\\"]+)\~\~")
        self._url_pattern = re.compile("\[([\w \.\,\!\;\:\-\'\\\"]+)\]\(([\w \.\,\!\;\:\/]+)\)")
        self._image_pattern = re.compile("!\[([\w \.\,\!\;\:\-\'\\\"]+)\]\(([\w \.\,\!\;\:\/]+)\)")

    def extract_urls(self):
        pass

    def get_cleaned_text(self, text):
        # clean header info
        text = self._main_header_pattern.sub('', text)
        text = self._subheader_pattern.sub('', text)
        # clean line breaks
        text = self._linebreak_pattern.sub('', text)
        # clean emphasis
        text = self._strong_emphasis_pattern.sub(r'\1', text)
        text = self._emphasis_pattern.sub(r'\1', text)
        text = self._strikethrough_pattern.sub(r'\1', text)
        text = self._inline_pattern.sub(r'\1', text)
        # ignore urls
        text = self._url_pattern.sub(r'\1', text)

        return text.strip().lstrip()

    def match_title(self, text):
        match = self._main_header_pattern.match(text)
        if match:
            return match.group(1)
        return ""

    def clean_math(self):
        # `$$` 
        pass

    def process(self, text,
                get_title=True,
                get_cleaned_text=True):

        if get_title:
            title = self.match_title(text)
        if get_cleaned_text:
            cleaned_text = self.get_cleaned_text(text)

        return title, cleaned_text

    def text_get_cleaned_text(self):
        # test Headers
        test = '# title'
        assert self.get_cleaned_text(test) == 'title'
        test = 'last sentence. # title2'
        assert self.get_cleaned_text(test) == 'last sentence. title2'
        test = 'last sentence.\n## title2'
        assert self.get_cleaned_text(test) == 'last sentence. title2'
        test = '#hashtag is this'
        assert self.get_cleaned_text(test) == '#hashtag is this'
        test = 'some #hashtag'
        assert self.get_cleaned_text(test) == 'some #hashtag'

        # test Emphasis
        test = "Emphasis, aka italics, with *asterisks* or _underscores_."
        res = self.get_cleaned_text(test)
        assert res == "Emphasis, aka italics, with asterisks or underscores."

        test = "Strong emphasis, aka bold, with **asterisks** or __underscores__."
        res = self.get_cleaned_text(test)
        assert res == "Strong emphasis, aka bold, with asterisks or underscores."

        test = "Combined emphasis with **asterisks and _underscores_**."
        res = self.get_cleaned_text(test)
        assert res == "Combined emphasis with asterisks and underscores."

        test = "Strikethrough uses two tildes. ~~Scratch this.~~"
        res = self.get_cleaned_text(test)
        assert res == "Strikethrough uses two tildes. Scratch this."

        test = "[I'm link](tes_url)"
        res = self.get_cleaned_text(test)
        assert res == "I'm link"

        test = "[I'm an inline-style link](https://www.google.com)"
        res = self.get_cleaned_text(test)
        assert res == "I'm an inline-style link"

        # inline
        test = 'some `inline` #items'
        res = self.get_cleaned_text(test)
        assert res == 'some inline #items'
