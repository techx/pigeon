import { Box, Grid, Stack, Text, Title, Divider, Button, Group } from "@mantine/core";
import { useState, useEffect } from "react";
import classes from './inbox.module.css';
import { RichTextEditor } from '@mantine/tiptap';
import { useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import Placeholder from "@tiptap/extension-placeholder";

interface Email {
    id: number;
    body: string;
    message_id: string;
    sender: string;
    subject: string;
    resolved: boolean;
}

export default function InboxPage() {
    const [emails, setEmails] = useState<Array<Email>>([]);
    const [active, setActive] = useState(-1);
    const [content, setContent] = useState("");

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
    })
    const getEmails = () => {
        fetch("/api/emails/get_emails")
            .then(res => res.json())
            .then(data => {
                console.log(data);
                setEmails(data);
            })
    }
    useEffect(() => {
        getEmails();
        const interval = setInterval(getEmails, 10000);
        return () => clearInterval(interval);
    }, []);
    useEffect(() => {
        console.log(content);
    }, [content])
    const sendEmail = () => {
        let formData = new FormData();
        formData.append('index', emails[active].id.toString());
        formData.append('body', content);
        fetch("/api/emails/send_email", {
            method: 'POST',
            body: formData
        });
        editor?.commands.clearContent(true)
    };

    const emailList = emails.map((email, index) => {
        const sender = email.sender.indexOf("<") !== -1 ? email.sender.split("<")[0].replace(/"/g, " ") : email.sender;
        return (
            <div key={email.id} onClick={() => {
                    setActive(index); 
                    setContent("");
                    editor?.commands.clearContent(true);
                }}>
                <Box className={classes.box + " " + (index == active ? classes.selected : "")} >
                    <Title size="md">{sender}</Title>
                    <Text>{email.subject}</Text>
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
                    {emailList}
                </Stack>
            </Grid.Col>
            <Grid.Col span={8} className={classes.grid}>
                {active != -1 && (
                    <Box>
                        <Title size="md">{emails[active].sender.replace(/"/g, "")}</Title>
                        <Text>{emails[active].subject}</Text>
                        <Text>{emails[active].body}</Text>

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
                        </Group>
                    </Box>  
                )}
            </Grid.Col>
        </Grid>
       </Box>
    );
}