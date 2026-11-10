# ADR 0003 — A tour's version is set by the developer

**Status:** accepted

## Decision

A tour carries a version, `Tour(version=...)`, a whole number of 1 or more that is 1 unless the
developer says otherwise. The browser's entry for a seen tour, under the key ADR 0002 sets, holds
the version that played. A browser whose entry holds any other version treats the tour as not
seen, plays it by itself once, and stores the declared version.

## Why

A changed tour has to reach the people who saw the old one, and a small edit must not.

- A version worked out from the steps, such as a hash, changes on every edit, so a typo fix would
  bring the tour back to everyone. Only the developer knows whether a change matters.
- Keeping the key as it is and storing the version as its value means a browser that saw a tour
  before versions existed, which holds `"1"`, still counts it as seen at the default version 1.
  Adding the version to the key would have played every tour on every site again once.
- Comparing for any difference, rather than for a higher number, means a lowered version, after a
  revert for example, also plays once, and nothing depends on versions only going up.

## Consequences

- A developer who forgets to raise the version after a large change shows it to nobody who saw the
  old one. The documentation says when to raise it.
- A tour declared with `autoplay=False` keeps waiting for the replay control at any version.

## Revisit if

- A site needs a changed tour to show only its new steps, rather than the whole tour again.
