# -*- coding: utf-8 -*-
# description for pyubersicht

import pathlib
import types

import jinja2

_DefaultDir = pathlib.Path('~/Library/Application Support/Übersicht/widgets').expanduser()

_Template = jinja2.Template('''
command: "{{command}}"

render: (output) -> """
{{render}}
"""

update: (output, domEl) -> """
{{update}}
"""

style: """
{{style}}
"""

refreshFrequency: {{refreshFrequency}}
''')

_DefaultStyle = """
  background: rgba(#fff, 0.5) url('übersicht-logo.png') no-repeat 50% 20px
  background-size: 176px 84px
  border-radius: 0px
  border: 0px solid #fff
  box-sizing: border-box
  color: #141f33
  font-family: Helvetica Neue
  font-weight: 300
  left: 50%
  line-height: 1.5
  margin-left: -170px
  padding: 120px 20px 20px
  top: 10%
  width: 340px
  text-align: justify

  h1
    font-size: 20px
    font-weight: 300
    margin: 16px 0 8px

  em
    font-weight: 400
    font-style: normal
"""

_DefaultParamters = {"command": "python3 widget_title/script.py", "render": "#{output}", "update":"#{output}", "refreshFrequency":"1000*3600", "style":_DefaultStyle}

class UbersichtBiulder(object):
    '''UbersichtBiulder has 1 (principal) proptery
    strategy: strategy
    '''
    path = _DefaultDir
    
    @classmethod
    def build(cls, widget):
        folder = cls.path / widget.title
        if not folder.exists():
            folder.mkdir()
        index = folder / 'index.coffee'
        index.touch()
        index.write_text(_Template.render(widget.parameter), encoding='utf-8')


class PyUbersichtBiulder(UbersichtBiulder):
    '''UbersichtBiulder has 1 (principal) proptery
    strategy: strategy
    '''

    @classmethod
    def build(cls, widget):
        widget.parameter['command'] = 'python3 %s/script.py'%widget.title
        super(PyUbersichtBiulder, cls).build(widget)
        script = cls.path / widget.title / 'script.py'
        script.touch()
        content = '''# -*- coding: utf-8 -*-

"""Python script for %s"""

print('hello world')'''%widget.title
        script.write_text(content)


class UbersichtWidget(object):
    '''UbersichtWidget has 3 (principal) propteries
    title: title
    description: description
    parameter: parameter
    '''

    def __init__(self, title='', description='', parameter={}):
        self.title = title
        self.description = description
        
        self.parameter = _DefaultParamters.copy()
        self.parameter.update(parameter)
        self.otherfiles = []
        self.folder = _DefaultDir / self.title

    def make(self):
        UbersichtBiulder.build(self)

    def select(self, builder=UbersichtBiulder):
        self.make = types.MethodType(builder.build, self)


class PyUbersichtWidget(UbersichtWidget):
    
    def __init__(self, title='', description='', parameter={}):
        updatestr = """
newout = 'Default Output'
exec "python3 %s -o output -d domEl", (err, stdout, stderr) -> newout=stdout
""" % (_DefaultDir / title / "update.py")
        parameter.update({'update': updatestr})
        super(PyUbersichtWidget, self).__init__(title, description, parameter)

    def make(self):
        PyUbersichtBiulder.build(self)
        script = self.folder / "update.py"
        script.touch()
        content = '''# -*- coding: utf-8 -*-
"""Python script for %s"""

import argparse
parser = argparse.ArgumentParser(description='Update desk.')
parser.add_argument('-o', dest='output', action='store', metavar='STRING', help='the current output')
parser.add_argument('-d', dest='domEl', action='store', metavar='STRING', help='DOM Elements')

args = parser.parse_args()

output = args.output
domEl = args.domEl

# (output, domEl) -> new output

print(output)'''%self.title
        script.write_text(content)


if __name__ == '__main__':
    
    # u = UbersichtWidget(title='schedule', description='a schedule for managing time.')
    # builder = PyUbersichtBiulder

    # builder.build(u)

    u = PyUbersichtWidget(title='myschedule', description='My own schedule.')
    u.make()
