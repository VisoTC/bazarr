import { useDeleteLogs, useSystemLogs } from "@/apis/hooks";
import { ContentHeader, QueryOverlay } from "@/components";
import { Environment } from "@/utilities";
import { faDownload, faSync, faTrash } from "@fortawesome/free-solid-svg-icons";
import { Container, Row } from "@mantine/core";
import { FunctionComponent, useCallback } from "react";
import { Helmet } from "react-helmet";
import Table from "./table";

const SystemLogsView: FunctionComponent = () => {
  const logs = useSystemLogs();
  const { isFetching, data, refetch } = logs;

  const { mutate, isLoading } = useDeleteLogs();

  const download = useCallback(() => {
    window.open(`${Environment.baseUrl}/bazarr.log`);
  }, []);

  return (
    <QueryOverlay result={logs}>
      <Container fluid>
        <Helmet>
          <title>Logs - Bazarr (System)</title>
        </Helmet>
        <ContentHeader>
          <ContentHeader.Button
            updating={isFetching}
            icon={faSync}
            onClick={() => refetch()}
          >
            Refresh
          </ContentHeader.Button>
          <ContentHeader.Button icon={faDownload} onClick={download}>
            Download
          </ContentHeader.Button>
          <ContentHeader.Button
            updating={isLoading}
            icon={faTrash}
            onClick={() => mutate()}
          >
            Empty
          </ContentHeader.Button>
        </ContentHeader>
        <Row>
          <Table logs={data ?? []}></Table>
        </Row>
      </Container>
    </QueryOverlay>
  );
};

export default SystemLogsView;
