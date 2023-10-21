import { useState, useEffect } from 'react';
import { Container, Textarea, TextInput, Button, Space, Card, Text, Group, Stack, ScrollArea, Box, Table } from '@mantine/core';
import { notifications } from "@mantine/notifications";
import classes from './documents.module.css';
import { useClickOutside } from '@mantine/hooks';

interface Document {
    id: number;
    label: string;
    question: string;
    content: string;
    source: string;
}

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Array<Document>>([]);
    const [question, setQuestion] = useState("");
    const [content, setContent] = useState("");
    const [source, setSource] = useState("");
    const [label, setLabel] = useState("");
    const [active, setActive] = useState(-1);
    const [search, setSearch] = useState("");

    const ref = useClickOutside(() => {setActive(-1); clearContent();});

    const getDocuments = () => {
        fetch("/api/admin/get_documents")
        .then(res => res.json())
        .then(data => {
            setDocuments(data);
        })
    };
    useEffect(() => {
        getDocuments();
    }, []);

    const clearContent = () => {
        getDocuments();
        setQuestion("");
        setContent("");
        setSource("");
        setLabel("");
    }
    const uploadDocument = () => {
        notifications.clean();
        if(!content || !source || !label) {
            notifications.show({
                title: "Error!",
                color: "red",
                message: "Fill all required fields!",
            });
            return;
        }
    
        let formData = new FormData();
        formData.append('question', question);
        formData.append('content', content);
        formData.append('source', source);
        formData.append('label', label);
        fetch("/api/admin/upload_document", {
            method: "POST",
            body: formData
        }).then(res => {
            if(res.ok) return res.json();
            notifications.show({
                title: "Error!",
                color: "red",
                message: "Something went wrong!",
              });
        }).then(data => {
            clearContent();
            notifications.show({
                title: "Success!",
                color: "green",
                message: data.message,
              });
        })
    };

    const editDocument = (id : number) => {
        notifications.clean();
        if(!content || !source || !label) {
            notifications.show({
                title: "Error!",
                color: "red",
                message: "Fill all required fields!",
            });
            return;
        }
    
        let formData = new FormData();
        formData.append('id', id.toString());
        formData.append('question', question);
        formData.append('content', content);
        formData.append('source', source);
        formData.append('label', label);
        fetch("/api/admin/edit_document", {
            method: "POST",
            body: formData
        }).then(res => {
            if(res.ok) return res.json();
            notifications.show({
                title: "Error!",
                color: "red",
                message: "Something went wrong!",
              });
        }).then(data => {
            getDocuments();
            notifications.show({
                title: "Success!",
                color: "green",
                message: data.message,
              });
        })
    }

    const deleteDocument = (id : number) => {
        notifications.clean();
        let formData = new FormData();
        formData.append('id', id.toString());
        fetch("/api/admin/delete_document", {
            method: "POST",
            body: formData
        }).then(res => {
            if(res.ok) return res.json();
            notifications.show({
                title: "Error!",
                color: "red",
                message: "Something went wrong!",
              });
        }).then(data => {
            clearContent();
            getDocuments();
            setActive(-1);
            notifications.show({
                title: "Success!",
                color: "green",
                message: data.message,
              });
        })
    }

    const handleSelect = (id : number) => {
        setActive(id);
        const activeDocument = documents.filter((document) => document.id === id)[0];
        setQuestion(activeDocument.question);
        setContent(activeDocument.content);
        setSource(activeDocument.source);
        setLabel(activeDocument.label);
    }
    const documentList = documents.map((document) => { 
        const cat = document.label.toLowerCase() + " " + document.question.toLowerCase() + " " + document.content.toLowerCase() + " " + document.source.toLowerCase();
        if(search && !cat.includes(search.toLowerCase())) return;
        return (
        <Table.Tr onClick = {() => handleSelect(document.id)}key={document.id} className={classes.row + " " + (active == document.id && classes.selected)}>
            <Table.Td>{document.label}</Table.Td>
            <Table.Td>{document.question == "" ? "N/A" : document.question}</Table.Td>
            <Table.Td>{document.content.length < 50 ? document.content : document.content.substring(0, 47) + "..."}</Table.Td>
        </Table.Tr>
    )});
    return (
        <Container ref={ref}>
            <Space h="xl"/>
            <TextInput disabled={active != -1} value={search} onChange={(e) => setSearch(e.target.value)} placeholder={"Search any field"} />
           <ScrollArea h={400}>
            <Table >
                <Table.Thead>
                    <Table.Tr>
                        <Table.Th>Label</Table.Th>
                        <Table.Th>Question</Table.Th>
                        <Table.Th>Content</Table.Th>
                    </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                    {documentList}
                </Table.Tbody>
                </Table>
                </ScrollArea>
            <Stack>
                <Group grow>
                    <TextInput required value={label} onChange={(e) => setLabel(e.target.value)} label="Label" />
                    <TextInput value={question} onChange={(e) => setQuestion(e.target.value)} label="Question (optional)"/>
                </Group>
                
                <Textarea required value={content} onChange={(e) => setContent(e.target.value)} minRows={2} autosize label="Content"/>
                <TextInput required value={source} onChange={(e) => setSource(e.target.value)} label="Source" />
                <Group>
                    {active == -1 ? (<Button onClick={() => uploadDocument()}>Upload New Document</Button>) : (<Button onClick={() => editDocument(active)}>Edit Document</Button>)}
                    {active != -1 && (<Button color="red" onClick={() => deleteDocument(active)}>Delete Document</Button>)}
                </Group>
            </Stack>
            
        </Container>
    );
}