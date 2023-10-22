import { Box, Grid, Stack, Text, Title, Divider, Button, Group, Timeline, ScrollArea, Modal, ThemeIcon } from "@mantine/core";
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
    sender: string;
    subject: string;
    reply: boolean;
    threadId: number;
}

export default function InboxPage() {
    const [threads, setThreads] = useState<Array<Thread>>([]);
    const [active, setActive] = useState(-1);
    const [content, setContent] = useState("");
    const activeThread = threads.filter((thread) => {return thread.id === active;})[0];
    const [threadSize, setThreadSize] = useState(activeThread ? activeThread.emailList.length : 0);
    const [opened, { open, close }] = useDisclosure(false);
    
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
    });
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
    


    const sendEmail = () => {
        notifications.clean();
        const formData = new FormData();
        formData.append('index', activeThread.emailList[activeThread.emailList.length-1].id.toString());
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

    useEffect(() => {
        if(activeThread && activeThread.emailList.length > threadSize){
            if(viewport && viewport.current) viewport.current!.scrollTo({top: viewport.current!.scrollHeight, behavior: "smooth"});
            setThreadSize(activeThread.emailList.length);
        }
    }, [active, threads])
    
    const threadList = threads.map((thread) => {
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
                    <Text>{thread.emailList[thread.emailList.length-1].subject}</Text>
                </Box>
                <Divider />
            </div>
        )
    });

    
    return (
     
        <Grid classNames={{inner: classes.grid_inner, root: classes.grid}} columns={100}>
            <Grid.Col span={40} className={classes.threads} >
                <Text className={classes.inboxText}>Inbox</Text>
                <Stack  gap={0}>
                    {threadList}
                </Stack>
            </Grid.Col>
            <Grid.Col span={58} className={classes.thread}>
                {active != -1 && (
                    <Box>
                        <Text className={classes.subjectText}>{activeThread.emailList[0].subject}</Text>
                        <ScrollArea className={classes.threadScroll} h={400} viewportRef={viewport}>
                            {/* TODO(azliu): MAIL_USERNAME */}
                        <Timeline active={Math.max(...activeThread.emailList.filter(email => email.sender === "help@my.hackmit.org").map(email => activeThread.emailList.indexOf(email)))}>
                            {activeThread.emailList.map((email) => (
                                <Timeline.Item key={email.id} bullet={email.sender == "help@my.hackmit.org" && (<ThemeIcon size={20} color="blue" radius="xl"></ThemeIcon>)}>
                                    <Title size="xl">{email.sender}</Title>
                                    <Text dangerouslySetInnerHTML={{__html: email.html}}/>
                                </Timeline.Item>
                            ))}
                        </Timeline>
                        </ScrollArea>
                        <Stack className={classes.editor}>
                        <RichTextEditor editor={editor}>
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
                            <RichTextEditor.Content className={classes.content}/>
                        </RichTextEditor>
                        <Modal size="60vw" opened={opened} onClose={close} title="Authentication">
                                {/* Modal content */}
                        </Modal>
                        <Group>
                            <Button onClick={() => sendEmail()}>Send</Button>
                            <Button color="green">Regenerate Response</Button>
                            <Button color="orange" onClick={open}>Show Sources</Button>
                        </Group>
                        </Stack>
                    </Box>  
                )}
            </Grid.Col>
        </Grid>
    
    );
}