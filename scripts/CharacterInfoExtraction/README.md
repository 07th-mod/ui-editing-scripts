Some scripts for figuring out what characters are used in games to help with choosing what characters to put on font atlases

I had originally made these for personal use and wasn't thinking about publishing them, so I wrote them in Swift, which doesn't currently support compiling on Windows.  Very sorry about that.  I guess you could try out WSL?

Download Swift [here](https://swift.org/download/) for Ubuntu or macOS, it also appears to be [on the AUR](https://aur.archlinux.org/packages/swift/) for Arch users and on the main Fedora repo as `swift-lang`.  Compile a script with `swiftc -O scriptFile.swift` or run it directly with `swift -O scriptFile.swift arguments`, though that will be fairly slow if you plan to run the script multiple times.

Documentation coming soon™

## Hou Plus Notes

Hou Plus uses a single font file for both languages, so you need to use the 'combined' list which contains both 'OtherLang' and Japanese characters `msgothic_2_charset_JP_and_OtherLang.txt`.