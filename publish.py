import json
import glob
import os.path
from datetime import datetime
from textwrap import dedent
import nbformat

from parser.markdown_parser import SimpleMarkdownParser
from parser.python3_parser import SimplePython3Parser


class Publisher():

    def __init__(self, content_path='content/', notebook_path='notebooks/', index_file='search/index.json'):
        self.published_contents = {}
        self.content_path = content_path
        self.notebook_path = notebook_path
        self.notebook_prefix = 'ipynb'
        self.meta_prefix = 'ipynb-meta'
        self.index_file = index_file
        self.index = {}
        self.content_template = dedent("""
            Title: {Title}
            Date: {Date}
            Modified: {Modified}
            Category: {Category}
            Tags: {Tags}
            Authors: {Authors}
            Summary: {Summary}
        """).lstrip().strip()

        self.md_parser = SimpleMarkdownParser()
        self.py3_parser = SimplePython3Parser()

    def get_modified_timestamp(self, file):
        return datetime.fromtimestamp(os.path.getmtime(file))

    def get_created_timestamp(self, file):
        return datetime.fromtimestamp(os.path.getctime(file))

    def load_notebook(self, notebook_filepath, nbformat_version=4):
        notebook = nbformat.read(notebook_filepath, as_version=nbformat_version)
        # check nbformat:
        if not notebook.nbformat == nbformat_version:
            notebook = nbformat.read(notebook_filepath, as_version=notebook.nbformat)
        return notebook

    def discover_notebooks(self):
        self.load_index()
        new_index = {}
        if not self.published_contents:
            self.load_published_contents()

        notebook_files = glob.glob(self.notebook_path + '*.' + self.notebook_prefix)
        for note_file in notebook_files:
            file_name = note_file[len(self.notebook_path):-len(self.notebook_prefix)-1]
            modified_time = self.get_modified_timestamp(note_file)
            if file_name in self.published_contents:
                # check timestamp
                if modified_time.strftime("%Y-%m-%d %H:%M") == \
                     self.published_contents[file_name].get('Modified', ''):
                    print('no change for {} '.format(file_name))
                    if file_name in self.index:
                        new_index[file_name] = self.index[file_name]
                    else:
                        notebook = self.load_notebook(note_file)
                        new_index[file_name] = self.build_index(notebook, file_name)
                else:
                    print('date not match for {}'.format(file_name))
                    new_meta_content = self.published_contents[file_name]
                    notebook = self.load_notebook(note_file)
                    new_meta_content['Modified'] = modified_time.strftime("%Y-%m-%d %H:%M")
                    self.write_meta_content(new_meta_content, file_name)
                    self.copy_notebook_to_content(notebook, file_name)
                    print('{} updated!'.format(file_name))
                    new_index[file_name] = self.build_index(notebook, file_name)

            else:
                print('found new one {}'.format(file_name))
                notebook = self.load_notebook(note_file)
                meta = self.build_meta(notebook)
                self.write_meta_content(meta, file_name)
                self.copy_notebook_to_content(notebook, file_name)
                print('{} published!'.format(file_name))
                new_index[file_name] = self.build_index(notebook, file_name)

        self.index = new_index
        self.save_index()

    def build_meta(self, notebook):
        # notebook - TODO fill this by info from notebook
        meta = {
                'Title': 'Test Title',
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Modified': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Category': ', '.join(['Cat1', 'Category 2']),
                'Tags': ', '.join(['Tag1', 'tag2 is the best']),
                'Authors': 'Ramtin Seraj',
                'Summary': 'Summary is the best '
                }
        return meta

    def load_published_contents(self):
        published_files = glob.glob(self.content_path + '*.' + self.meta_prefix)
        for file in published_files:
            file_name = file[len(self.content_path):-len(self.meta_prefix)-1]
            # check if notebook file exist:
            prefix = '.' + self.notebook_prefix
            file_path = self.content_path + file_name + prefix
            if os.path.isfile(file_path):
                self.published_contents[file_name] = self.read_meta_file(file)

    def copy_notebook_to_content(self, notebook, file_name, remove_outputs=False):
        if remove_outputs:
            remove_metadata_fields = {'collapsed', 'scrolled'}
            for cell in notebook.cells or []:
                if cell.cell_type == "code":
                    cell.outputs = []
                    cell.execution_count = None
                    # Remove metadata associated with output
                    if 'metadata' in cell:
                        for field in remove_metadata_fields:
                            cell.metadata.pop(field, None)

        # write to file
        file_path = self.content_path + file_name + '.' + self.notebook_prefix
        with open(file_path, 'w') as outp:
            json.dump(notebook, outp, indent=4)

    def write_meta_content(self, meta_data, file_name):
        content_text = self.content_template.format(**meta_data)
        file_path = self.content_path + file_name + '.' + self.meta_prefix
        with open(file_path, 'w') as outp:
            outp.write(content_text)

    def read_meta_file(self, file_path):
        content_meta = {}
        with open(file_path) as inp:
            for line in inp:
                line = line.strip()
                if line and ':' in line:
                    key, value = line.split(':', 1)
                    content_meta[key] = value.lstrip()
                else:
                    print('Unknown line format : ')
                    print(line)
        return content_meta

    def load_index(self):
        if os.path.isfile(self.index_file):
            with open(self.index_file) as inp:
                data = json.load(inp)
                for page in data.get('pages', []):
                    id = page.get('id')
                    self.index[id] = page

    def save_index(self):
        data = []
        for value in self.index.values():
            data.append(value)

        with open(self.index_file, 'w') as outp:
            json.dump({'pages': data}, outp, indent=4)

    def build_index(self, notebook, file_name):
        # TODO this part
        index_data = {
            "text": "Lorem ipsum dolor sit amet",
            "tags": "Example Category",
            "url": "http://oncrashreboot.com/plugin-example.html",
            "id": file_name,
            "title": "Everything you want to know about Lorem Ipsum"
        }
        return index_data

    def process_notebook(self, notebook):
        meta = notebook.metadata
        lang = meta.get('language_info', {}).get('name')
        lang_version = meta.get('language_info', {}).get('version')

        for cell in notebook.cells or []:
            cell_type = cell.get('cell_type')
            if cell_type == "heading":
                title = cell.get('source')
            elif cell_type == "markdown":

                # self.md_parser

                res = clean_md(cell.get('source'))
                if not title:
                    title = res[1]
                    print('title')  # TODO
                    print(title)

                fulltext += '\n' + res[0]
            elif cell_type == "code":
                # process python code
                if lang == 'python' and lang_version.startswith('2.'):
                    packages, classes, methods = parse_python2_code(cell.get('source'))
                    if packages:
                        print(packages)
                    if classes:
                        print(classes)


if __name__ == "__main__":
    Publisher().discover_notebooks()
    # add data to tipue search
