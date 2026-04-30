import { SendMessageCommand, SQSClient } from "@aws-sdk/client-sqs";
import {
  Injectable,
  Logger,
  ServiceUnavailableException,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import type { JobEnvelope } from "@frodo/contracts";

@Injectable()
export class SqsService {
  private readonly logger = new Logger(SqsService.name);
  private readonly client: SQSClient | null;
  private readonly queueUrl: string | undefined;
  private readonly sqsRequired: boolean;

  constructor(private readonly config: ConfigService) {
    this.sqsRequired = this.config.get<boolean>("sqsRequired") ?? true;
    this.queueUrl = this.config.get<string>("SQS_QUEUE_URL");
    const region = this.config.get<string>("AWS_REGION");
    if (region && this.queueUrl) {
      this.client = new SQSClient({ region });
    } else {
      this.client = null;
    }
    if (this.sqsRequired && (!this.client || !this.queueUrl)) {
      throw new Error(
        "Invariant: sqsRequired but SQS client could not be initialized",
      );
    }
  }

  /**
   * Enqueue a job. Fails closed when SQS is required but not configured.
   * In development with ALLOW_ASYNC_SKIP=true, throws ServiceUnavailableException.
   */
  async sendJob(envelope: JobEnvelope): Promise<void> {
    if (!this.client || !this.queueUrl) {
      const msg =
        "Cannot enqueue background job: SQS is not configured (set AWS_REGION + SQS_QUEUE_URL, or use APP_ENV=development with ALLOW_ASYNC_SKIP=true only for local dev)";
      this.logger.error(`${msg} envelope=${envelope.type}`);
      throw new ServiceUnavailableException(msg);
    }

    await this.client.send(
      new SendMessageCommand({
        QueueUrl: this.queueUrl,
        MessageBody: JSON.stringify(envelope),
      }),
    );
    this.logger.debug(`Enqueued ${envelope.type}`);
  }
}
