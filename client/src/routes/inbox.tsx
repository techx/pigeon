import {
  Box,
  Grid,
  Stack,
  Text,
  Title,
  Divider,
  Button,
  Group,
  Timeline,
  ScrollArea,
  Flex,
  ThemeIcon,
  Progress,
  Accordion,
  Center,
} from "@mantine/core";
import { useState, useEffect, useRef } from "react";
import classes from "./inbox.module.css";
import { RichTextEditor } from "@mantine/tiptap";
import { useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import Placeholder from "@tiptap/extension-placeholder";
import { notifications } from "@mantine/notifications";
import {
  IconSend,
  IconRepeat,
  IconFolderOpen,
  IconFolderOff,
  IconCheck,
  IconX,
} from "@tabler/icons-react";

interface Thread {
  id: number;
  emailList: Email[];
  resolved: boolean;
}

interface Email {
  id: number;
  body: string;
  html: string;
  messageId: string;
  date: string;
  sender: string;
  subject: string;
  reply: boolean;
  threadId: number;
}

interface Document {
  label: string;
  question: string;
  content: string;
  source: string;
  confidence: number;
  to_delete: boolean;
  response_count: number;
}
interface Response {
  id: number;
  content: string;
  questions: string[];
  documents: Document[][];
  confidence: number;
  emailId: number;
}

export default function InboxPage() {
  const [threads, setThreads] = useState<Array<Thread>>([]);
  const [active, setActive] = useState(-1);
  const [content, setContent] = useState("");
  const activeThread = threads.filter((thread) => {
    return thread.id === active;
  })[0];
  const [threadSize, setThreadSize] = useState(
    activeThread ? activeThread.emailList.length : 0
  );
  const [sourceActive, setSourceActive] = useState(false);

  const [response, setResponse] = useState<Response | undefined>(undefined);

  const viewport = useRef<HTMLDivElement>(null);

  const editor = useEditor(
    {
      extensions: [
        StarterKit,
        Underline,
        Placeholder.configure({ placeholder: "Sample response..." }),
      ],
      onUpdate({ editor }) {
        setContent(editor.getHTML());
      },
      content: content,
    },
    [response]
  );
  const getThreads = () => {
    fetch("/api/emails/get_threads")
      .then((res) => res.json())
      .then((data) => {
        setThreads(data);
      });
  };
  useEffect(() => {
    getThreads();
    const interval = setInterval(getThreads, 300000);
    return () => clearInterval(interval);
  }, []);
  const strip: (text: string) => string = (text) => {
    return text.replace(/(<([^>]+)>)/gi, "");
  };
  const computeColor = (confidence: number | undefined) => {
    if (!confidence) return "rgba(255,0,0,1)";
    const red = [255, 0, 0];
    const green = [0, 255, 0];
    return `rgba(${red[0] + confidence * (green[0] - red[0])}, ${
      red[1] + confidence * (green[1] - red[1])
    }, ${red[2] + confidence * (green[2] - red[2])})`;
  };

  // dates are stored in UTC in server. display ET on client
  const parseDate = (date: string) => {
    const d = new Date(date);
    if (d.getDay() === new Date().getDay())
      return d.toLocaleTimeString("en-US", { timeZone: "America/New_York" });
    else return d.toLocaleDateString("en-US", { timeZone: "America/New_York" });
  };
  const parseFullDate = (date: string) => {
    const d = new Date(date);
    return d.toLocaleString("en-US", { timeZone: "America/New_York" });
  };
  const parseBody = (body: string) => {
    const lines = body.replace(new RegExp("\r?\n", "g"), "<br />");
    const linesArray = lines.split("<br />");
    return (
      <Text>
        {linesArray.map((line, idx) => {
          return (
            <div
              key={idx}
              dangerouslySetInnerHTML={{
                __html: line === "" ? "&nbsp;" : line,
              }}
            />
          );
        })}
      </Text>
    );
  };

  const getResponse = () => {
    const formData = new FormData();
    formData.append(
      "id",
      activeThread.emailList[activeThread.emailList.length - 1].id.toString()
    );
    fetch("/api/emails/get_response", {
      method: "POST",
      body: formData,
    })
      .then((res) => {
        if (res.ok) return res.json();
        notifications.show({
          title: "Error!",
          color: "red",
          message: "Something went wrong!",
        });
      })
      .then((data) => {
        setResponse(data);
        setContent(data.content.replaceAll("\n", "<br/>"));
      });
  };
  useEffect(() => {
    if (activeThread && !activeThread.resolved) getResponse();
  }, [active]);

  const sendEmail = () => {
    const strippedContent = strip(content);
    if (strippedContent.length < 10) {
      notifications.show({
        title: "Error!",
        color: "red",
        message: "Your response must be at least 10 characters long!",
      });
      return;
    }

    notifications.clean();
    notifications.show({
      id: "loading",
      title: "Loading",
      color: "blue",
      message: "Sending email...",
      loading: true,
      autoClose: false,
    });
    const formData = new FormData();
    formData.append(
      "id",
      activeThread.emailList[activeThread.emailList.length - 1].id.toString()
    );
    formData.append("body", content);
    fetch("/api/emails/send_email", {
      method: "POST",
      body: formData,
    })
      .then((res) => {
        if (res.ok) return res.json();
        notifications.update({
          id: "loading",
          title: "Error!",
          color: "red",
          message: "Something went wrong!",
        });
        setSourceActive(false);
      })
      .then((data) => {
        editor?.commands.clearContent(true);
        getThreads();
        notifications.update({
          id: "loading",
          title: "Success!",
          color: "green",
          message: data.message,
        });
        setSourceActive(false);
      });
  };

  const regenerateResponse = () => {
    const formData = new FormData();
    formData.append("id", active.toString());
    notifications.show({
      id: "loading",
      title: "Loading",
      color: "blue",
      message: "Generating response...",
      loading: true,
      autoClose: false,
    });
    fetch("/api/emails/regen_response", {
      method: "POST",
      body: formData,
    })
      .then((res) => {
        if (res.ok) return res.json();
        notifications.show({
          id: "loading",
          title: "Error!",
          color: "red",
          message: "Something went wrong!",
        });
      })
      .then(() => {
        getResponse();
        notifications.show({
          id: "loading",
          title: "Success!",
          color: "green",
          message: "Response has been regenerated!",
        });
      });
  };

  const resolveThread = () => {
    notifications.show({
      id: "loading",
      title: "Loading",
      color: "yellow",
      message: "Resolving thread...",
      loading: true,
      autoClose: false,
    });
    const formData = new FormData();
    formData.append("id", active.toString());
    fetch("/api/emails/resolve", {
      method: "POST",
      body: formData,
    })
      .then((res) => {
        if (res.ok) return res.json();
        notifications.show({
          id: "loading",
          title: "Error!",
          color: "red",
          message: "Something went wrong!",
        });
      })
      .then(() => {
        setThreads((oldThreads) => {
          return oldThreads.map((thread) => {
            if (thread.id === active) {
              thread.resolved = true;
            }
            return thread;
          });
        });
        setResponse(undefined);
        setContent("");
        notifications.update({
          id: "loading",
          title: "Success!",
          color: "green",
          message: "Resolved thread",
          autoClose: 2000,
          withCloseButton: false,
        });
      });
  };

  const unresolveThread = () => {
    notifications.show({
      id: "loading",
      title: "Loading",
      color: "yellow",
      message: "Unresolving thread...",
      loading: true,
      autoClose: false,
    });
    const formData = new FormData();
    formData.append("id", active.toString());
    fetch("/api/emails/unresolve", {
      method: "POST",
      body: formData,
    })
      .then((res) => {
        if (res.ok) return res.json();
        notifications.update({
          id: "loading",
          title: "Error!",
          color: "red",
          message: "Something went wrong!",
        });
      })
      .then(() => {
        setThreads((oldThreads) => {
          return oldThreads.map((thread) => {
            if (thread.id === active) {
              thread.resolved = false;
            }
            return thread;
          });
        });
        getResponse();
        notifications.update({
          id: "loading",
          title: "Success!",
          color: "green",
          message: "Unresolved thread",
          autoClose: 2000,
          withCloseButton: false,
        });
      });
  };

  useEffect(() => {
    if (activeThread && activeThread.emailList.length > threadSize) {
      if (viewport && viewport.current)
        viewport.current!.scrollTo({
          top: viewport.current!.scrollHeight,
          behavior: "smooth",
        });
      setThreadSize(activeThread.emailList.length);
      if (!activeThread.resolved) getResponse();
    }
    if (threads.length > 0 && active === -1) {
      const actualThreads = threads
        .filter((thread) => thread.emailList.length > 0)
        .map((thread) => thread.id);
      if (actualThreads.length > 0) {
        setActive(Math.min(...actualThreads));
      }
    }
  }, [active, threads]);

  const cmpDate: (a: string, b: string) => number = (a, b) => {
    const d1 = new Date(a as string | number | Date);
    const d2 = new Date(b as string | number | Date);
    return d1.getTime() < d2.getTime() ? 1 : -1;
  };

  const sortThreads: (a: Thread, b: Thread) => number = (a, b) => {
    if (a.resolved && !b.resolved) return 1;
    if (!a.resolved && b.resolved) return -1;
    if (
      a.emailList.length > 0 &&
      b.emailList.length > 0 &&
      a.emailList[a.emailList.length - 1] &&
      a.emailList[a.emailList.length - 1].date &&
      b.emailList[b.emailList.length - 1] &&
      b.emailList[b.emailList.length - 1].date
    )
      return cmpDate(
        a.emailList[a.emailList.length - 1].date,
        b.emailList[b.emailList.length - 1].date
      );
    else return -1;
  };

  const threadList = threads.sort(sortThreads).map((thread) => {
    if (thread.emailList.length === 0) return <></>;
    const sender =
      thread.emailList[thread.emailList.length - 1].sender.indexOf("<") !== -1
        ? thread.emailList[thread.emailList.length - 1].sender
            .split("<")[0]
            .replace(/"/g, " ")
        : thread.emailList[thread.emailList.length - 1].sender;
    return (
      <div
        key={thread.id}
        onClick={() => {
          if (active !== thread.id) {
            setContent("");
            editor?.commands.clearContent(true);
            setActive(thread.id);
            setThreadSize(
              threads.filter((newThread) => {
                return thread.id === newThread.id;
              })[0].emailList.length
            );
          }
        }}
      >
        <Box
          className={
            classes.box +
            " " +
            (thread.id === active ? classes.selected : "") +
            " " +
            (!thread.resolved ? classes.unresolved : "")
          }
        >
          <Title size="md">{sender}</Title>
          <Flex className={classes.between}>
            <Text>{thread.emailList[thread.emailList.length - 1].subject}</Text>
            <Text>
              {parseDate(thread.emailList[thread.emailList.length - 1].date)}
            </Text>
          </Flex>
          <Text className={classes.preview}>
            {strip(thread.emailList[thread.emailList.length - 1].body)}
          </Text>
        </Box>
        <Divider />
      </div>
    );
  });

  const sourceList = response?.questions.map((question, index) => {
    return (
      <div key={index}>
        <Text className={classes.sourceQuestion}>
          {"Question: " + question}
        </Text>
        <Accordion>
          {response.documents[index].map((document, documentIndex) => {
            return (
              <Accordion.Item
                style={{
                  "border-left": `6px solid ${computeColor(
                    // Math.round((document.confidence / 0.8) * 100) / 100
                    Math.round(document.confidence * 100) / 100
                  )}`,
                }}
                key={documentIndex}
                value={
                  document.label.length === 0
                    ? "Unlabeled Document " + documentIndex
                    : document.label + " " + documentIndex
                }
              >
                <Accordion.Control>
                  {document.label.length === 0
                    ? "Unlabeled Document"
                    : document.label}
                  <Text className={classes.sourceConfidence}>
                    {"Relevance: " +
                      // Math.round((document.confidence / 0.8) * 100) / 100
                      Math.round(document.confidence * 100) / 100}
                  </Text>
                  {document.to_delete && (
                    <Text className={classes.deletedWarning}>
                      {
                        "This source has been deleted! Regenerating response recommended."
                      }
                    </Text>
                  )}
                </Accordion.Control>
                <Accordion.Panel>
                  <div>
                    {document.question.length > 0 && (
                      <Text className={classes.sourceText}>
                        {document.question}
                      </Text>
                    )}
                    <Text className={classes.sourceText}>
                      {document.content}
                    </Text>
                    <Text>Source: ({document.source})</Text>
                    {/* Change source to links in the future */}
                  </div>
                </Accordion.Panel>
              </Accordion.Item>
            );
          })}
        </Accordion>
      </div>
    );
  });

  return (
    <Grid
      classNames={{ inner: classes.grid_inner, root: classes.grid }}
      columns={100}
    >
      {!sourceActive && (
        <Grid.Col span={30} className={classes.threads}>
          <Text className={classes.inboxText}>Inbox</Text>
          <Stack gap={0} className={classes.threadList}>
            {threadList}
          </Stack>
        </Grid.Col>
      )}

      <Grid.Col span={sourceActive ? 58 : 68} className={classes.thread}>
        {active !== -1 && (
          <Box>
            <Center className={classes.subjectText}>
              {"Subject: " + activeThread.emailList[0].subject}
            </Center>
            {/* <Stack className={classes.threadList}> */}
            <ScrollArea
              className={classes.threadScroll}
              h={400}
              viewportRef={viewport}
            >
              {/* TODO(azliu): make help@my.hackmit.org an environment variable */}
              <Timeline
                active={Math.max(
                  ...activeThread.emailList
                    .filter(
                      (email) =>
                        email.sender ===
                        '"Blueprint Team" <blueprint@my.hackmit.org>'
                    )
                    .map((email) => activeThread.emailList.indexOf(email))
                )}
              >
                {activeThread.emailList.map((email) => (
                  <Timeline.Item
                    key={email.id}
                    bullet={
                      email.sender ===
                        '"Blueprint Team" <blueprint@my.hackmit.org>' && (
                        <ThemeIcon
                          size={20}
                          color="blue"
                          radius="xl"
                        ></ThemeIcon>
                      )
                    }
                  >
                    <Flex className={classes.between}>
                      <Title size="xl">{email.sender}</Title>
                      <Text>{parseFullDate(email.date)}</Text>
                    </Flex>
                    {parseBody(email.body)}
                  </Timeline.Item>
                ))}
              </Timeline>
            </ScrollArea>
            <Stack className={classes.editor}>
              {activeThread && !activeThread.resolved && (
                <Group>
                  <Text>Response Confidence</Text>
                  <Progress.Root size={30} style={{ width: "70%" }}>
                    <Progress.Section
                      value={
                        response === undefined || response.confidence < 0
                          ? 0
                          : Math.round(response.confidence * 125)
                      }
                      color={computeColor(response?.confidence)}
                    >
                      <Progress.Label>
                        {response === undefined || response.confidence < 0
                          ? "0"
                          : Math.round(response.confidence * 125)}
                        %
                      </Progress.Label>
                    </Progress.Section>
                  </Progress.Root>
                </Group>
              )}
              <RichTextEditor
                classNames={{ content: classes.content }}
                editor={editor}
              >
                <RichTextEditor.Toolbar sticky stickyOffset={60}>
                  <RichTextEditor.ControlsGroup>
                    <RichTextEditor.Bold />
                    <RichTextEditor.Italic />
                    <RichTextEditor.Underline />
                  </RichTextEditor.ControlsGroup>

                  <RichTextEditor.ControlsGroup>
                    <RichTextEditor.H1 />
                    <RichTextEditor.H2 />
                    <RichTextEditor.H3 />
                    <RichTextEditor.H4 />
                  </RichTextEditor.ControlsGroup>

                  <RichTextEditor.ControlsGroup>
                    <RichTextEditor.BulletList />
                    <RichTextEditor.OrderedList />
                  </RichTextEditor.ControlsGroup>

                  <RichTextEditor.ControlsGroup>
                    <RichTextEditor.Link />
                    <RichTextEditor.Unlink />
                  </RichTextEditor.ControlsGroup>
                </RichTextEditor.Toolbar>
                <RichTextEditor.Content />
              </RichTextEditor>

              <Group>
                <Button leftSection={<IconSend />} onClick={() => sendEmail()}>
                  Send
                </Button>
                {!activeThread.resolved && (
                  <Button
                    leftSection={<IconRepeat />}
                    onClick={() => regenerateResponse()}
                    color="green"
                  >
                    Regenerate Response
                  </Button>
                )}
                {!activeThread.resolved && (
                  <Button
                    leftSection={
                      sourceActive ? <IconFolderOff /> : <IconFolderOpen />
                    }
                    color="orange"
                    onClick={() => setSourceActive(!sourceActive)}
                  >
                    {sourceActive ? "Close Sources" : "Open Sources"}
                  </Button>
                )}

                {!activeThread.resolved && (
                  <Button
                    leftSection={<IconCheck />}
                    color="yellow"
                    onClick={() => resolveThread()}
                  >
                    Resolve
                  </Button>
                )}

                {activeThread.resolved && (
                  <Button
                    leftSection={<IconX />}
                    color="red"
                    onClick={() => unresolveThread()}
                  >
                    Unresolve
                  </Button>
                )}
              </Group>
            </Stack>
          </Box>
        )}
      </Grid.Col>
      {sourceActive && (
        <Grid.Col span={42} className={classes.threads}>
          <Text className={classes.inboxText}>Sources</Text>
          <ScrollArea h="95vh">{sourceList}</ScrollArea>
        </Grid.Col>
      )}
    </Grid>
  );
}
