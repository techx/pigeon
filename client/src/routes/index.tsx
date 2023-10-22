import { Box, Container, Flex, Center, Text, Anchor, Space } from "@mantine/core";
import classes from './index.module.css';

export default function IndexPage() {
  return (
    <Flex direction="column">
      <Space h="xl"></Space>
      <Container mx="auto" size="lg" className={classes.wrapper}>
        <Text className={classes.top}>
          Pigeon
        </Text>
        <Text className={classes.subtext}>
          Welcome to Pigeon, an AI-powered email assistant!
        </Text>
        <Box>
          <Text className={classes.sectionHeader}> How do I use Pigeon? </Text>
          <Center>
            <Text className={classes.text}>
              If you run into any other issues please email us at{" "}
              <Anchor target="_blank" href="mailto:help@hackmit.org" c="blue">help@my.hackmit.org</Anchor>.
            </Text>
          </Center>
        </Box>
      </Container>
    </Flex>
  );
}