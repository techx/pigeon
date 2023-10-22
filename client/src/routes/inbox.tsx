import { Box, Grid, Stack, Text, Title, Divider, Button, Group, Timeline, ScrollArea, Flex, Modal, ThemeIcon, Progress, Center } from "@mantine/core";
import { useState, useEffect, useRef } from "react";
import classes from './inbox.module.css';
import { RichTextEditor } from '@mantine/tiptap';
import { useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import Placeholder from "@tiptap/extension-placeholder";
import { notifications } from "@mantine/notifications";
import { useDisclosure } from '@mantine/hooks';

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

interface Response {
    id: number;
    content: string;
    questions: string[];
    documents: string[];
    documentsConfidence: number[];
    confidence: number;
    emailId: number;
}

export default function InboxPage() {
    const [threads, setThreads] = useState<Array<Thread>>([]);
    const [active, setActive] = useState(-1);
    const [content, setContent] = useState("");
    const activeThread = threads.filter((thread) => {return thread.id === active;})[0];
    const [threadSize, setThreadSize] = useState(activeThread ? activeThread.emailList.length : 0);
    const [opened, { open, close }] = useDisclosure(false);
    const [response, setResponse] = useState<Response | undefined>(undefined);

    const viewport = useRef<HTMLDivElement>(null);

    const editor = useEditor({
        extensions: [
            StarterKit,
            Underline,
            Placeholder.configure({ placeholder: "Sample response..." })
        ],
        onUpdate({ editor }) {
            setContent(editor.getHTML());
        },
        content: content,
    }, [response]);
    const getThreads = () => {
        fetch("/api/emails/get_threads")
            .then(res => res.json())
            .then(data => {
                setThreads(data);
            });
    };
    useEffect(() => {
        getThreads();
        const interval = setInterval(getThreads, 10000);
        return () => clearInterval(interval);
    }, []);
    const strip: (text: String) => String = (text) => {
        return text.replace(/(<([^>]+)>)/gi, "");
    }
    const computeColor = (confidence : number | undefined) => {
        if (!confidence) return 'rgba(255,0,0,1)'
        const red = [255, 0, 0];
        const green = [0, 255, 0];
        return `rgba(${red[0] + confidence * (green[0] - red[0])}, ${red[1] + confidence * (green[1] - red[1])}, ${red[2] + confidence * (green[2] - red[2])})`
    }
    const parseDate = (date : string) => {
        const d = new Date(date);
        return d.toLocaleString();
    }

    const getResponse = () => {
        const formData = new FormData();
        formData.append('id', activeThread.emailList[activeThread.emailList.length-1].id.toString());
        fetch("/api/emails/get_response", {
            method: 'POST',
            body: formData
        })
            .then(res => {
                if(res.ok) return res.json();
                notifications.show({
                    title: "Error!",
                    color: "red",
                    message: "Something went wrong!",
                });
            })
            .then(data => {
                setResponse(data);
                setContent(data.content.replaceAll("\n", "<br/>"));
            })
    }   
    useEffect(() => {
        if(activeThread && !activeThread.resolved) getResponse();
    }, [active]);


    const sendEmail = () => {
        const strippedContent = strip(content);
        if(strippedContent.length < 10){
            notifications.show({
                title: "Error!",
                color: "red",
                message: "Your response must be at least 10 characters long!",
              });
            return;
        }

        notifications.clean();
        const formData = new FormData();
        formData.append('id', activeThread.emailList[activeThread.emailList.length-1].id.toString());
        formData.append('body', content);
        fetch("/api/emails/send_email", {
            method: 'POST',
            body: formData
        }).then(res => {
            if(res.ok) return res.json();
            notifications.show({
                title: "Error!",
                color: "red",
                message: "Something went wrong!",
              });
        }).then(data => {
            editor?.commands.clearContent(true);
            getThreads();
            notifications.show({
                title: "Success!",
                color: "green",
                message: data.message,
              });
        });
        
    };

    const regenerateResponse = () => {
        const formData = new FormData();
        formData.append('id', active.toString());
        notifications.show({
            id: 'loading',
            title: "Loading",
            color: "blue",
            message: "Generating response...",
            loading: true,
            autoClose: false,
        })
        fetch("/api/emails/regen_response", {
            method: 'POST',
            body: formData
        }).then(res => {
            if(res.ok) return res.json();
            notifications.hide('loading');
            notifications.show({
                title: "Error!",
                color: "red",
                message: "Something went wrong!",
              });
        }).then(data => {
            setResponse(data);
            setContent(data.content.replaceAll("\n", "<br/>"));
            notifications.hide('loading');
            notifications.show({
                title: "Success!",
                color: "green",
                message: "Response has been regenerated!",
            });
        });
    };

    useEffect(() => {
        if(activeThread && activeThread.emailList.length > threadSize){
            if(viewport && viewport.current) viewport.current!.scrollTo({top: viewport.current!.scrollHeight, behavior: "smooth"});
            setThreadSize(activeThread.emailList.length);
            if (!activeThread.resolved) getResponse();
        }
        if (threads.length > 0 && active === -1) {
            const actualThreads = threads.filter(thread => thread.emailList.length > 0).map(thread => thread.id);
            if (actualThreads.length > 0) {
                setActive(Math.min(...actualThreads));
            }
        }
    }, [active, threads])
    
    const threadList = threads.map((thread) => {
        if(thread.emailList.length === 0) return (<></>);
        const sender = thread.emailList[thread.emailList.length-1].sender.indexOf("<") !== -1 ? thread.emailList[thread.emailList.length-1].sender.split("<")[0].replace(/"/g, " ") : thread.emailList[thread.emailList.length-1].sender;
        return (
            <div key={thread.id} onClick={() => {
                    setContent("");
                    editor?.commands.clearContent(true);
                    setActive(thread.id);
                    setThreadSize(threads.filter((newThread) => {return thread.id === newThread.id;})[0].emailList.length);
                }}>
                <Box className={classes.box + " " + (thread.id === active ? classes.selected : "") + " " + (!thread.resolved ? classes.unresolved : "")} >
                    <Title size="md">{sender}</Title>
                    <Flex className={classes.between}>
                        <Text>{thread.emailList[thread.emailList.length-1].subject}</Text>
                        <Text>{parseDate(thread.emailList[thread.emailList.length-1].date)}</Text>
                    </Flex>
                    <Text className={classes.preview}>{strip(thread.emailList[thread.emailList.length-1].body)}</Text>
                </Box>
                <Divider />
            </div>
        )
    });

    
    return (
        <Grid classNames={{inner: classes.grid_inner, root: classes.grid}} columns={100}>
            <Grid.Col span={25} className={classes.threads} >
                <Center className={classes.inboxText}>Inbox</Center>
                <Stack gap={0} className={classes.threadList}>
                    {threadList}
                </Stack>
            </Grid.Col>
            <Grid.Col span={73} className={classes.thread}>
                {active !== -1 && (
                    <Box>
                        <Center className={classes.subjectText}>{activeThread.emailList[0].subject}</Center>
                        {/* <Stack className={classes.threadList}> */}
                        <ScrollArea className={classes.threadScroll} h={400} viewportRef={viewport}>
                            {/* TODO(azliu): make help@my.hackmit.org an environment variable */}
                            <Timeline active={Math.max(...activeThread.emailList.filter(email => email.sender === "help@my.hackmit.org").map(email => activeThread.emailList.indexOf(email)))}>
                                {activeThread.emailList.map((email) => (
                                    <Timeline.Item key={email.id} bullet={email.sender === "help@my.hackmit.org" && (<ThemeIcon size={20} color="blue" radius="xl"></ThemeIcon>)}>
                                        <Title size="xl">{email.sender}</Title>
                                        <Text dangerouslySetInnerHTML={{__html: email.html}}/>
                                    </Timeline.Item>
                                ))}
                            </Timeline>
                        </ScrollArea>
                        <Stack className={classes.editor}>
                            {activeThread && !activeThread.resolved && <Group>
                                <Text>Response Confidence</Text>
                                <Progress.Root size={30} style={{width: "70%"}}>
                                    <Progress.Section value={response === undefined || response.confidence < 0 ? 0: Math.round(response.confidence * 100)} color={computeColor(response?.confidence)}>
                                    <Progress.Label>{response === undefined || response.confidence < 0 ? "0": Math.round(response.confidence * 100)}%</Progress.Label>
                                    </Progress.Section>
                                </Progress.Root>
                            </Group>}
                            <RichTextEditor classNames={{content: classes.content}} editor={editor}>
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
                                    <RichTextEditor.Content/>
                                </RichTextEditor>
                                <Modal size="60vw" opened={opened} onClose={close} title="Source Documents">
                                        {/* Modal content */}
                                </Modal>
                                <Group>
                                    <Button onClick={() => sendEmail()}>Send</Button>
                                    {!activeThread.resolved && (<Button onClick={() => regenerateResponse()} color="green">Regenerate Response</Button>)} 
                                    {!activeThread.resolved && (<Button color="orange" onClick={open}>Show Sources</Button>)}
                                </Group>
                            </Stack>
                        {/* </Stack> */}
                    </Box>  
                )}
            </Grid.Col>
        </Grid>
    
    );
}