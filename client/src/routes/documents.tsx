import { useState, useEffect } from "react";
import {
  Container,
  Textarea,
  TextInput,
  Button,
  Text,
  Group,
  Stack,
  ScrollArea,
  Table,
  FileButton,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import classes from "./documents.module.css";
import { useClickOutside } from "@mantine/hooks";
import { IconSearch } from "@tabler/icons-react";

interface Document {
  id: number;
  label: string;
  question: string;
  content: string;
  source: string;
}

import { BASE_URL } from "../main";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Array<Document>>([]);
  const [question, setQuestion] = useState("");
  const [content, setContent] = useState("");
  const [source, setSource] = useState("");
  const [label, setLabel] = useState("");
  const [active, setActive] = useState(-1);
  const [search, setSearch] = useState("");

  const ref = useClickOutside(() => {
    setActive(-1);
    if (active !== -1) clearContent();
  });

  const getDocuments = () => {
    fetch(`${BASE_URL}/api/admin/get_documents`)
      .then((res) => res.json())
      .then((data) => {
        setDocuments(data);
      });
  };
  useEffect(() => {
    getDocuments();
  }, []);

  const updateEmbeddings = () => {
    fetch(`${BASE_URL}/api/admin/update_embeddings`);
  };

  const clearContent = () => {
    getDocuments();
    setQuestion("");
    setContent("");
    setSource("");
    setLabel("");
  };

  const uploadJSON = (file: File | null) => {
    notifications.clean();
    if (!file) {
      notifications.show({
        title: "Error!",
        color: "red",
        message: "No file selected!",
      });
      return;
    }
    // const formData = new FormData();
    // formData.append("file", file);
    // console.log(formData);
    fetch(`${BASE_URL}/api/admin/upload_json`, {
      method: "POST",
      body: file,
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
        clearContent();
        notifications.show({
          title: "Success!",
          color: "green",
          message: data.message,
        });
      })
      .then(updateEmbeddings);
  };

  const importCSV = (file: File | null) => {
    notifications.clean();
    if (!file) {
      notifications.show({
        title: "Error!",
        color: "red",
        message: "No file selected!",
      });
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    // console.log(formData);
    fetch(`${BASE_URL}/api/admin/import_csv`, {
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
        clearContent();
        notifications.show({
          title: "Success!",
          color: "green",
          message: data.message,
        });
      })
      .then(updateEmbeddings);
  };

  const uploadDocument = () => {
    notifications.clean();
    if (!content || !source || !label) {
      notifications.show({
        title: "Error!",
        color: "red",
        message: "Fill all required fields!",
      });
      return;
    }

    const formData = new FormData();
    formData.append("question", question);
    formData.append("content", content);
    formData.append("source", source);
    formData.append("label", label);
    console.log(formData);
    fetch(`${BASE_URL}/api/admin/upload_document`, {
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
        clearContent();
        notifications.show({
          title: "Success!",
          color: "green",
          message: data.message,
        });
      })
      .then(updateEmbeddings);
  };

  const editDocument = (id: number) => {
    notifications.clean();
    if (!content || !source || !label) {
      notifications.show({
        title: "Error!",
        color: "red",
        message: "Fill all required fields!",
      });
      return;
    }

    const formData = new FormData();
    formData.append("id", id.toString());
    formData.append("question", question);
    formData.append("content", content);
    formData.append("source", source);
    formData.append("label", label);
    fetch(`${BASE_URL}/api/admin/edit_document`, {
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
        getDocuments();
        notifications.show({
          title: "Success!",
          color: "green",
          message: data.message,
        });
      })
      .then(updateEmbeddings);
  };

  const deleteDocument = (id: number) => {
    notifications.clean();
    const formData = new FormData();
    formData.append("id", id.toString());
    fetch(`${BASE_URL}/api/admin/delete_document`, {
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
        clearContent();
        getDocuments();
        setActive(-1);
        notifications.show({
          title: "Success!",
          color: "green",
          message: data.message,
        });
      })
      .then(updateEmbeddings);
  };
  const clearDocuments = () => {
    notifications.clean();
    fetch(`${BASE_URL}/api/admin/clear_documents`, {
      method: "POST",
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
        clearContent();
        getDocuments();
        setActive(-1);
        notifications.show({
          title: "Success!",
          color: "green",
          message: data.message,
        });
      })
      .then(updateEmbeddings);
  };

  const handleSelect = (id: number) => {
    setActive(id);
    const activeDocument = documents.filter(
      (document) => document.id === id
    )[0];
    setQuestion(activeDocument.question);
    setContent(activeDocument.content);
    setSource(activeDocument.source);
    setLabel(activeDocument.label);
  };
  const documentList = documents.map((document) => {
    const cat =
      document.label.toLowerCase() +
      " " +
      document.question.toLowerCase() +
      " " +
      document.content.toLowerCase() +
      " " +
      document.source.toLowerCase();
    if (search && !cat.includes(search.toLowerCase())) return;
    return (
      <Table.Tr
        onClick={() => handleSelect(document.id)}
        key={document.id}
        className={
          classes.row + " " + (active === document.id && classes.selected)
        }
      >
        <Table.Td>{document.label}</Table.Td>
        <Table.Td>
          {document.question === "" ? "N/A" : document.question}
        </Table.Td>
        <Table.Td>{document.content}</Table.Td>
      </Table.Tr>
    );
  });
  return (
    <Container ref={ref}>
      <Text className={classes.title}>Documents</Text>
      <TextInput
        className={classes.search}
        leftSection={<IconSearch size={20} />}
        disabled={active !== -1}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder={"Search any field"}
      />
      <ScrollArea h={400}>
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Label</Table.Th>
              <Table.Th>Question</Table.Th>
              <Table.Th>Content</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{documentList}</Table.Tbody>
        </Table>
      </ScrollArea>
      <Stack className={classes.stack}>
        <Group grow>
          <TextInput
            required
            value={label}
            placeholder="Shower"
            onChange={(e) => setLabel(e.target.value)}
            label="Label"
          />
          <TextInput
            value={question}
            placeholder="Can we shower at HackMIT?"
            onChange={(e) => setQuestion(e.target.value)}
            label="Question (optional)"
          />
        </Group>

        <Textarea
          required
          value={content}
          placeholder="The HackMIT venue will not have showering facilities available for hackers to use."
          onChange={(e) => setContent(e.target.value)}
          minRows={2}
          autosize
          label="Content"
        />
        <TextInput
          required
          value={source}
          placeholder="https://hackmit.org/"
          onChange={(e) => setSource(e.target.value)}
          label="Source"
        />
        <Group>
          {active === -1 ? (
            <Button onClick={() => uploadDocument()}>
              Upload New Document
            </Button>
          ) : (
            <Button onClick={() => editDocument(active)}>Edit Document</Button>
          )}
          {active === -1 ? (
            <FileButton
              onChange={(file) => uploadJSON(file)}
              accept="file/json"
            >
              {(props) => {
                return (
                  <Button {...props} color="green">
                    Upload JSON
                  </Button>
                );
              }}
            </FileButton>
          ) : (
            <Button color="red" onClick={() => deleteDocument(active)}>
              Delete Document
            </Button>
          )}
          {active === -1 && (
            <FileButton onChange={(file) => importCSV(file)} accept="file/csv">
              {(props) => {
                return (
                  <Button {...props} color="cyan">
                    Import CSV
                  </Button>
                );
              }}
            </FileButton>
          )}
          {active === -1 && (
            <Button color="orange" onClick={() => clearDocuments()}>
              Clear Documents
            </Button>
          )}
        </Group>
      </Stack>
    </Container>
  );
}
