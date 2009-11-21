# An element of this array (a "solution") describes a repository directory
# that will be checked out into your working copy.  Each solution may
# optionally define additional dependencies (via its DEPS file) to be
# checked out alongside the solution's directory.  A solution may also
# specify custom dependencies (via the "custom_deps" property) that
# override or augment the dependencies specified by the DEPS file.
# If a "safesync_url" is specified, it is assumed to reference the location of
# a text file which contains nothing but the last known good SCM revision to
# sync against. It is fetched if specified and used unless --head is passed

solutions = [
  { "name"        : "chromiumos.git",
    "url"         : "http://src.chromium.org/git/chromiumos.git",
    "custom_deps" : {
      # To use the trunk of a component instead of what's in DEPS:
      #"component": "https://svnserver/component/trunk/",
      # To exclude a component from your working copy:
      #"data/really_large_component": None,
    },
    "safesync_url": ""
  },
]
