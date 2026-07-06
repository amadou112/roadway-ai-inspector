import { DesignReviewDetailClient } from "./DesignReviewDetailClient";

export default async function DesignReviewDetailPage({
  params,
}: {
  params: Promise<{ submissionId: string }>;
}) {
  const { submissionId } = await params;
  return <DesignReviewDetailClient submissionId={submissionId} />;
}
