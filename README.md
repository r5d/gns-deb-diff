# gns-deb-diff

This script is an effort to automate the documentation of the
differences between gNewSense and Debian.

The present list of differences is documented at the
[gNewSense wiki][1]. Look at the [savannah task #12794][2] for more
info.

[1]: http://www.gnewsense.org/Documentation/3/DifferencesWithDebian
[2]: https://savannah.nongnu.org/task/?12794

## Synopsis

    $ python gns-deb-diff.py packages-list-file output-table-file local-packages-directory remote-bzr-url

**defaults**

    local-packages-directory = "~/gnewsense/packages-parkes"
    remote-bzr-url = "bzr://bzr.savannah.gnu.org/gnewsense/packages-parkes"

`packages-list-file`, is a file which contains a list of package names
that differ from Debian. Look at `packages-parkes.list` file for a
sample.

`output-table-file`, is the file to which the script should write the
difference table.

## Description

This is what the script does at present:

+   **S1** The script pulls the latest version of the packages, listed
    in the `packages-list-file`, from their respective bzr repos.

+   **S2** For packages which contain the `README.gNewSense` file, a
    dict of the form `{'pkg': 'package_name', 'Change-Type':
    'Added/Removed/Modified', 'Changed-From-Debian': 'one line
    description'}` is generated.

    The value for keys `Change-Type` & `Changed-Frome-Debian` is None,
	if values for those are not present in the `README.gNewSense`.

+   **S3** The script puts the names of packages, which doesn't contain
    `README.gNewSense` file, into a seperate list.

+   **S4** The dicts produced in **S2** is used to generate
    MoinMoin marked up table, like
    [the one found here][gns-deb-diff-notes].

+   **S5** The generated table is written to the `output-table-file`.

+   **S4** The list of packages which doesn't contain `README.gNewSense`
    is barfed out to stdout.

[gns-deb-diff-notes]: http://www.gnewsense.org/sddhrth/gns-deb-diff-notes

## Notes

At present, not all packages contain a `README.gNewSense` file. It'd
nice, if all packages that were modified/removed/added in gNewSense
have this file.

See [here for more][gns-deb-diff-notes].

## License

The script is under the [WTFPL version 2 license][3]. See COPYING for more
details. This license is [compatible with GNU GPL][4].

[3]: http://www.wtfpl.net/txt/copying/
[4]: http://www.gnu.org/licenses/license-list.html#WTFPL
