import json
import glob
import os.path
from datetime import datetime
from textwrap import dedent
import nbformat

from parsers.markdown_parser import SimpleMarkdownParser
from parsers.python3_parser import SimplePython3Parser

from collections import namedtuple


class Meta():
    def __init__(self,
                 id,
                 title=None,
                 date=None,
                 modified=None,
                 category=None,
                 tags=[],
                 authors=[],
                 summary=None,
                 cleaned_text="",
                 url=None):
        self.id = id
        self.title = title
        if not self.title:
            self.title = id.replace('_', ' ').replace('-', ' ')
        self.date = date
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.modified = modified
        if not self.modified:
            self.modified = self.date
        self.category = category
        self.tags = tags
        self.authors = authors
        self.summary = summary
        self.cleaned_text = cleaned_text
        self.url = url

    def load_markdown_string(self, text):
        for line in text.split('\n'):
            line = line.strip()
            if line and ':' in line:
                key, value = line.split(':', 1)
                if key == 'Title':
                    self.title = value.lstrip()
                elif key == 'Date':
                    self.date = value.lstrip()
                elif key == 'Modified':
                    self.modified = value.lstrip()
                elif key == 'Category':
                    self.category = value.lstrip()
                elif key == 'Tags':
                    self.tags = [item.strip().lstrip() for item in value.split(',')]
                elif key == 'Authors':
                    self.authors = [item.strip().lstrip() for item in value.split(',')]
                elif key == 'Summary':
                    self.summary = value.lstrip()
            else:
                print('Unknown line format: {}'.format(line))

    def load_markdown_file(self, file_path):
        if not os.path.isfile(file_path):
            print('File does not exist {}'.format(file_path))
        else:
            with open(file_path) as inp:
                text = inp.read()
                self.load_markdown_string(text)

    def dump_markdown_string(self):
        markdown_string = ""
        if self.title:
            markdown_string += "Title: {}\n".format(self.title)
        if self.date:
            markdown_string += "Date: {}\n".format(self.date)
        if self.modified:
            markdown_string += "Modified: {}\n".format(self.modified)
        if self.category:
            markdown_string += "Category: {}\n".format(self.category)
        if self.tags:
            markdown_string += "Tags: {}\n".format(', '.join(self.tags))
        if self.authors:
            markdown_string += "Authors: {}\n".format(', '.join(self.authors))
        if self.id:
            markdown_string += "Slug: {}\n".format(self.id)
        if self.summary:
            markdown_string += "Summary: {}\n".format(self.summary)
        return markdown_string

    def dump_markdown_file(self, file_path):
        with open(file_path, 'w') as outp:
            data = self.dump_markdown_string()
            outp.write(data)


class Publisher():

    def __init__(self,
                 content_path='content/',
                 notebook_path='notebooks/',
                 index_file_path='output/search/index.json',
                 notebook_prefix='ipynb',
                 meta_prefix='ipynb-meta',
                 default_author='Ramtin Seraj'):
        self.content_path = content_path
        self.notebook_path = notebook_path
        self.index_file_path = index_file_path
        self.published_meta = {}
        self.notebook_prefix = notebook_prefix
        self.meta_prefix = meta_prefix
        self.default_author = default_author

        self.md_parser = SimpleMarkdownParser()
        self.py3_parser = SimplePython3Parser()

    def _get_modified_timestamp(self, file):
        return datetime.fromtimestamp(os.path.getmtime(file))

    def _get_created_timestamp(self, file):
        return datetime.fromtimestamp(os.path.getctime(file))

    def _load_notebook(self, notebook_filepath, nbformat_version=4):
        notebook = nbformat.read(notebook_filepath, as_version=nbformat_version)
        # check nbformat:
        if not notebook.nbformat == nbformat_version:
            notebook = nbformat.read(notebook_filepath, as_version=notebook.nbformat)
        return notebook

    def _load_published_meta(self):
        published_files = glob.glob(self.content_path + '*.' + self.meta_prefix)
        for file in published_files:
            file_name = file[len(self.content_path):-len(self.meta_prefix)-1]
            # check if notebook file exist:
            file_path = self.content_path + file_name + '.' + self.notebook_prefix
            if os.path.isfile(file_path):
                meta = Meta(file_name)
                meta.load_markdown_file(file)
                self.published_meta[file_name] = meta

    def _load_index(self):
        if os.path.isfile(self.index_file_path):
            with open(self.index_file_path) as inp:
                data = json.load(inp)
                for page in data.get('pages', []):
                    id = page.get('id')
                    if id in self.published_meta:
                        self.published_meta[id].cleaned_text = page.get('text')
                        self.published_meta[id].url = page.get('url')

    def _save_index(self):
        data = []
        for meta in self.published_meta.values():
            data.append({
                "text": meta.cleaned_text,
                "tags": ', '.join(meta.tags),
                "url": meta.url,
                "id": meta.id,
                "title": meta.title
                })
        with open(self.index_file_path, 'w') as outp:
            json.dump({'pages': data}, outp, indent=4)

    def _discover_notebooks(self):
        notebook_files = glob.glob(self.notebook_path + '*.' + self.notebook_prefix)
        for note_file in notebook_files:
            file_name = note_file[len(self.notebook_path):-len(self.notebook_prefix)-1]
            date_time = self._get_created_timestamp(note_file).strftime("%Y-%m-%d %H:%M")
            modified_time = self._get_modified_timestamp(note_file).strftime("%Y-%m-%d %H:%M")
            if file_name in self.published_meta:
                # check timestamp
                if modified_time == self.published_meta[file_name].modified:
                    print('no change for {} '.format(file_name))
                else:
                    print('date not match for {}'.format(file_name))
                    notebook = self._load_notebook(note_file)
                    meta = self._publish_new_notebook(notebook, file_name, date_time, modified_time)
                    self._copy_notebook_to_content(notebook, file_name)
                    meta_file_path = self.content_path + file_name + '.' + self.meta_prefix
                    meta.dump_markdown_file(meta_file_path)
                    self.published_meta[file_name] = meta
                    print('{} updated!'.format(file_name))
            else:
                print('found new one {}'.format(file_name))
                notebook = self._load_notebook(note_file)
                meta = self._publish_new_notebook(notebook, file_name, date_time, modified_time)
                self._copy_notebook_to_content(notebook, file_name)
                meta_file_path = self.content_path + file_name + '.' + self.meta_prefix
                meta.dump_markdown_file(meta_file_path)
                self.published_meta[file_name] = meta
                print('{} published!'.format(file_name))

    def _publish_new_notebook(self, notebook, file_name, date, modified):
        lang = notebook.metadata.get('language_info', {}).get('name')
        lang_version = notebook.metadata.get('language_info', {}).get('version')

        title = ""
        summary = ""  # first
        cleaned_text = ""
        category = None
        tags = []
        for cell in notebook.cells or []:
            cell_type = cell.get('cell_type')
            if cell_type == "heading":
                title = cell.get('source')
            elif cell_type == "markdown":
                res = self.md_parser.process(cell.get('source'))
                if not title:
                    title = res[0]
                if not summary:
                    summary = res[1]
                cleaned_text += '\n' + res[1]
            elif cell_type == "code":
                # process python code
                if lang == 'python':
                    category = "python"
                if lang == 'python' and lang_version.startswith('2.'):
                    packages, classes, methods = self.py3_parser.process(cell.get('source'))
                    for p in packages:
                        tags += ['python_package: {}'.format(p)]
                    if classes:
                        print(classes)

        meta = Meta(id=file_name,
                    title=title,
                    date=date,
                    modified=modified,
                    tags=tags,
                    authors=[self.default_author],
                    cleaned_text=cleaned_text,
                    url='{}.html'.format(file_name)
                    )
        if category:
            meta.category = category
        if summary:
            meta.summary = summary
        return meta

    def _copy_notebook_to_content(self, notebook, file_name, remove_outputs=False):
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

    def publish(self):
        self._load_published_meta()
        print(self.published_meta)
        self._load_index()
        self._discover_notebooks()
        self._save_index()

if __name__ == "__main__":
    Publisher().publish()
    # add data to tipue search
