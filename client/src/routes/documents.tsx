import { useState, useEffect } from 'react';
import { Container, Textarea, TextInput, Button, Space, Card, Text, Group, Stack, ScrollArea, Box, Table } from '@mantine/core';
import { notifications } from "@mantine/notifications";

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


    const getDocuments = () => {
        fetch("/api/admin/get_documents")
        .then(res => res.json())
        .then(data => {
            console.log(data);
            setDocuments(data);
        })
    };
    useEffect(() => {
        getDocuments();
    }, []);

    const uploadDocument = () => {
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
            getDocuments();
            setQuestion("");
            setContent("");
            setSource("");
            setLabel("");
            notifications.show({
                title: "Success!",
                color: "green",
                message: data.message,
              });
        })
    };

    
    const documentList = documents.map((document) => (
        <Table.Tr  key={document.id}>
            <Table.Td>{document.label}</Table.Td>
            <Table.Td>{document.question == "" ? "None" : document.question}</Table.Td>
            <Table.Td>{document.content.length < 50 ? document.content : document.content.substring(0, 47) + "..."}</Table.Td>
        </Table.Tr>
    ));
    return (
        <Container>
            <Space h="xl"/>
            
            <Table.ScrollContainer minWidth={500}>
            <Table>
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
            </Table.ScrollContainer>
            
            <Stack>
                <Group grow>
                    <TextInput value={label} onChange={(e) => setLabel(e.target.value)} label="Label" />
                    <TextInput value={question} onChange={(e) => setQuestion(e.target.value)} label="Question (optional)"/>
                </Group>
                
                <Textarea value={content} onChange={(e) => setContent(e.target.value)} minRows={2} autosize label="Content"/>
                <TextInput value={source} onChange={(e) => setSource(e.target.value)} label="Source" />
                <Button onClick={() => uploadDocument()}>Upload</Button>
            </Stack>
            
        </Container>
    );
}