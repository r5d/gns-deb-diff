# gns-deb-diff

This script is an effort to automate the documentation of the
differences between gNewSense and Debian.

The present list of differences is documented at the
[gNewSense wiki][2]. Look at the [savannah task #12794][1] for more
info.

[1]: https://savannah.nongnu.org/task/?12794
[2]: http://www.gnewsense.org/Documentation/3/DifferencesWithDebian

## Synopsis

    $ python gns-deb-diff.py packages-list-file output-table-file local-packages-directory remote-bzr-url

**defaults**

    local-packages-directory = "~/gnewsense/packages-parkes"
    remote-bzr-url = "bzr://bzr.savannah.gnu.org/gnewsense/packages-parkes"

`packages-list-file`, is a file which contains a list of package names
that differ from Debian. Look at `packages-parkes.list` file for a
sample.

`output-table-file`, is the file to which the script should write the difference table.

## Description

This is what the script does at present:

+ **S1** The script pulls the latest version of the packages, listed
in the `packages-list-file`, from their respective bzr repos.

+ **S2** For packages which contain the `README.gNewSense` file, it
reads the content into a dict; the keys being the names of the
packages.

+ **S3** The script puts the names of packages, which doesn't contain
`README.gNewSense` file, into a seperate list.

+ **S4** The dict produced in **S2** is used to generate MoinMoin
marked up table, like [the one here][2].

+ **S5** The generated table is written to the `output-table-file`.

+ **S4** The list of packages which doesn't contain `README.gNewSense`
is barfed out to stdout.

## Notes

1.  At present the script reads the whole `README.gNewSense` file and
    puts it in the second column of the table. The file is typically
    about 10 lines big & contains newlines.

    Unforunately, the MoinMoin markup for the table doesn't allow the
    columns to have new lines. So, the table generated by the script, at
    present, must be manually edited to remove newlines.

    A possible solution would be to have a one line description, of
    how the respective package differs from Debian, at the beginning of
    the `README.gNewSense`. This line can then be used by the script to
    generate the table.

2.  At present, not all packages contain a `README.gNewSense`
    file. It'd nice, if all packages that were modified/removed/added
    in gNewSense have this file.


## License

The script is under the [WTFPL version 2 license][3]. See COPYING for more
details. This license is [compatible with GNU GPL][4].

[3]: http://www.wtfpl.net/txt/copying/
[4]: http://www.gnu.org/licenses/license-list.html#WTFPL
