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
}

export default function InboxPage() {
    const [threads, setThreads] = useState<Array<Thread>>([]);
    const [active, setActive] = useState(-1);
    const [content, setContent] = useState("");
    const activeThread = threads.filter((thread) => {thread.id == active})[0];

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
        let formData = new FormData();
        formData.append('index', threads[activeThread.id].email_list[-1].id.toString());
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

    // const EmailList = ({threadId} : {threadId: number}) => {
    //     const threadEmails = threads[threadId].email_list;
    //     return (
    //         <Timeline>
    //             {threadEmails.map((email) => (
    //                 <Timeline.Item>
    //                     <Title size="md">{email.sender}</Title>
    //                     <Text>{email.subject}</Text>
    //                 </Timeline.Item>
    //             ))}
    //         </Timeline>
    //     )};


    // const emailList = threads.map((thread, index) => {
    //     //const sender = email.sender.indexOf("<") !== -1 ? email.sender.split("<")[0].replace(/"/g, " ") : email.sender;
    //     const sender = "asdf";
    //     return (
    //         <div key={index} onClick={() => {
    //                 setActive(index); 
    //                 setContent("");
    //                 editor?.commands.clearContent(true);
    //             }}>
    //             <Box>
    //                 <EmailList threadId={threads[index].id}/>
    //             </Box>
    //             <Divider />
    //         </div>
    //     )
    // });

    
    return (
       <Box>
        <Grid>
            <Grid.Col span={4} className={classes.grid}>
                <Stack  gap={0}>
                    {/* {emailList} */}
                </Stack>
            </Grid.Col>
            <Grid.Col span={8} className={classes.grid}>
                {active != -1 && (
                    <Box>
                        {/* <Title size="md">{activeEmail.sender.replace(/"/g, "")}</Title>
                        <Text>{activeEmail.subject}</Text>
                        <Text>{activeEmail.body}</Text> */}

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