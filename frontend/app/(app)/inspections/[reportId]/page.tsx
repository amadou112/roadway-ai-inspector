import { InspectionDetailClient } from "./InspectionDetailClient";

export default async function InspectionDetailPage({
  params,
}: {
  params: Promise<{ reportId: string }>;
}) {
  const { reportId } = await params;
  return <InspectionDetailClient reportId={reportId} />;
}
