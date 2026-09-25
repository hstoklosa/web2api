import { ScrollArea } from "@mantine/core";
import { defaultStyles, JsonView } from "react-json-view-lite";

import classes from "./json-viewer.module.css";

const styles = {
  ...defaultStyles,
  container: classes.container,
  basicChildStyle: classes.child,
  childFieldsContainer: classes.childFields,
  label: classes.label,
  clickableLabel: `${classes.label} ${classes.clickable}`,
  nullValue: classes.null,
  undefinedValue: classes.null,
  stringValue: classes.string,
  numberValue: classes.number,
  booleanValue: classes.boolean,
  otherValue: classes.other,
  punctuation: classes.punctuation,
  expandIcon: `${classes.icon} ${classes.expandIcon}`,
  collapseIcon: `${classes.icon} ${classes.collapseIcon}`,
  collapsedContent: classes.collapsedContent,
};

// Open the top two levels, so a list of records shows each record's fields
// while anything nested deeper starts folded.
const shouldExpandNode = (level: number) => level < 2;

type JsonViewerProps = {
  data: object;
};

export const JsonViewer = ({ data }: JsonViewerProps) => {
  return (
    <ScrollArea.Autosize
      mah={320}
      className={classes.root}
    >
      <JsonView
        data={data}
        style={styles}
        shouldExpandNode={shouldExpandNode}
        clickToExpandNode
      />
    </ScrollArea.Autosize>
  );
};
