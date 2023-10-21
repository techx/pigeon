import { Box, Grid, Stack, Text, Title, Divider, Button, Group, Timeline } from "@mantine/core";
import { useState, useEffect } from "react";
import classes from './inbox.module.css';
import { RichTextEditor } from '@mantine/tiptap';
import { useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import Placeholder from "@tiptap/extension-placeholder";
import { notifications } from "@mantine/notifications";

interface Thread {
    id: number;
    email_list: Email[];
}

interface Email {
    id: number;
    body: string;
    message_id: string;
    sender: string;
    subject: string;
    resolved: boolean;
    reply: boolean;
}

export default function InboxPage() {
    const [threads, setThreads] = useState<Array<Thread>>([]);
    const [active, setActive] = useState(-1);
    const [content, setContent] = useState("");
    const activeThread = threads.filter((thread) => {return thread.id === active;})[0];

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
                console.log(data);
                setThreads(data);
            })
    };
    useEffect(() => {
        getThreads();
        const interval = setInterval(getThreads, 10000);
        return () => clearInterval(interval);
    }, []);
    


    const sendEmail = () => {
        const formData = new FormData();
        formData.append('index', activeThread.email_list[activeThread.email_list.length-1].id.toString());
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
            console.log(data);
            notifications.show({
                title: "Success!",
                color: "green",
                message: data.message,
              });
        });
        
    };

    const threadList = threads.map((thread) => {
        const sender = thread.email_list[thread.email_list.length-1].sender.indexOf("<") !== -1 ? thread.email_list[thread.email_list.length-1].sender.split("<")[0].replace(/"/g, " ") : thread.email_list[thread.email_list.length-1].sender;
        return (
            <div key={thread.id} onClick={() => {
                    setActive(thread.id); 
                    setContent("");
                    editor?.commands.clearContent(true);
                }}>
                <Box className={classes.box + " " + (thread.id === active ? classes.selected : "") + (!thread.email_list[thread.email_list.length-1].resolved && !thread.email_list[thread.email_list.length-1].reply ? classes.unresolved : "")} >
                    <Title size="md">{sender}</Title>
                    <Text>{thread.email_list[thread.email_list.length-1].subject}</Text>
                </Box>
                <Divider />
            </div>
        )
    });

    
    return (
       <Box>
        <Grid>
            <Grid.Col span={4} className={classes.grid}>
                <Stack  gap={0}>
                    {threadList}
                </Stack>
            </Grid.Col>
            <Grid.Col span={8} className={classes.grid}>
                {active != -1 && (
                    <Box>
                        <Timeline>
                            {activeThread.email_list.map((email) => (
                                <Timeline.Item key={email.id}>
                                    <Title size="md">{email.sender}</Title>
                                    <Text>{email.subject}</Text>
                                    <Text dangerouslySetInnerHTML={{__html: email.body}}/>
                                </Timeline.Item>
                            ))}
                        </Timeline>

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
                            <RichTextEditor.Content />
                        </RichTextEditor>

                        <Group>
                            <Button>Generate</Button>
                            <Button onClick={() => sendEmail()}>Send</Button>
                            <Button onClick={() => {}}>Mark as Unresolved</Button>
                        </Group>
                    </Box>  
                )}
            </Grid.Col>
        </Grid>
       </Box>
    );
}