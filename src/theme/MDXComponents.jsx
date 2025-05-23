import React from 'react';
// Import the original mapper
import MDXComponents from '@theme-original/MDXComponents';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { library } from '@fortawesome/fontawesome-svg-core';
import { fab } from '@fortawesome/free-brands-svg-icons';
import { far } from '@fortawesome/free-regular-svg-icons';
import { fas } from '@fortawesome/free-solid-svg-icons';
import Link from '@docusaurus/Link';

import Button from '@site/src/components/Button';
import Columns from '@site/src/components/Columns';
import Column from '@site/src/components/Column';
import Figure from '@site/src/components/Figures';
import SmallInline from '@site/src/components/SmallInline';

// Add all icons to the library so you can use them without importing them individually.
library.add(fab, far, fas);

export default {
  // Re-use the default mapping
  ...MDXComponents,
  Button,
  Columns,
  Column,
  Figure,
  Link,
  SmallInline,
  FAIcon: FontAwesomeIcon,
};
