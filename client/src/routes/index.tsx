import {
  Box,
  Container,
  Flex,
  Center,
  Text,
  Anchor,
  Space,
  List,
} from "@mantine/core";
import classes from "./index.module.css";

export default function IndexPage() {
  return (
    <Flex direction="column">
      <Space h="xl"></Space>
      <Container size="lg" className={classes.wrapper}>
        <Text className={classes.top}>Pigeon</Text>
        <Text className={classes.subtext}>
          Welcome to Pigeon, your AI-powered email assistant!
        </Text>
        <Box>
          <Text className={classes.sectionHeader}> How do I use Pigeon? </Text>

          <List>
            <List.Item className={classes.text}>
              Use the documents tab to store all relevant documents to your
              event!
            </List.Item>
            <List.Item className={classes.text}>
              In the inbox, you can view all incoming help messages along with a
              customed AI-generated response based on relevant documents.
            </List.Item>
            <List.Item className={classes.text}>
              Use the inbox to keep track of threads and unresolved emails.
            </List.Item>
            <List.Item className={classes.text}>
              Each document is assigned a relevance score to the original
              question which together form an overall confidence value for the
              response.
            </List.Item>
            <List.Item className={classes.text}>
              You can then edit the response and send the final email as a
              response!
            </List.Item>
          </List>

          <Center>
            <Text className={classes.text + " " + classes.bottom}>
              If you run into any other issues please email us at{" "}
              <Anchor target="_blank" href="mailto:help@hackmit.org" c="blue">
                help@hackmit.org
              </Anchor>
              .
            </Text>
          </Center>
        </Box>
      </Container>
    </Flex>
  );
}
