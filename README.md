# AliveTree

AliveTree is a utility to assist the user in the process of making well formatted and good looking Kindle e-books.
It allows to export an OpenOffice/LibreOffice Writer document to a set of files fit for further processing with Amazon's Kindlegen utility.
The output from Kindlegen is compliant with the Amazon Kindle Publishing Guidelines. 

&copy;2013 Nicolò Tambone

## Installing AliveTree

Since AliveTree is written in Python, it's assumed you have Python 2.7 installed on your system.

## Usage 

Usage is very simple, e.g.:
alivetree -l en -i mydocument.odt

After the processing, which is very fast, you'll find some other files in the same directory. You can edit them manually to better fit your needs and you know what to do, but it's not necessary. The output files are ready to be compiled with Kindlegen. Assuming you have Kindlegen installed and in your path, just type at the command line (e.g.):

kindlegen content.opf [plus whatever parameters you like]

Then you'll find mydocument.mobi. That's it.

## Runtime Dependencies

WARNING: This software depends on [Beautiful Soup 4](https://pypi.python.org/pypi/beautifulsoup4).

## Notes

This project is still in a very early stage and there's place for a lot of improvements. 
Currently the only elements from the .odt source file being processed are only paragraphs and headings. Any other items, such images or table are being ignored. Though this is enaugh to cover about the 90% of fiction and poetry books, still it would be nice to implement those features in future releases.

## License

MIT License

