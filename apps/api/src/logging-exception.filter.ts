import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  HttpStatus,
  Logger,
} from "@nestjs/common";
import type { Response } from "express";

/**
 * Logs unexpected errors (non-HttpException and 5xx HttpException) so local
 * debugging isn't limited to the default Nest handler output.
 */
@Catch()
export class LoggingExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(LoggingExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<{ method?: string; url?: string }>();

    if (exception instanceof HttpException) {
      const status = exception.getStatus();
      if (status >= 500) {
        this.logger.error(
          `${request.method ?? "?"} ${request.url ?? "?"} → ${status}`,
          exception instanceof Error ? exception.stack : exception,
        );
      }
      response.status(status).json(exception.getResponse());
      return;
    }

    this.logger.error(
      `Unhandled ${request.method ?? "?"} ${request.url ?? "?"}`,
      exception instanceof Error ? exception.stack : exception,
    );
    response.status(HttpStatus.INTERNAL_SERVER_ERROR).json({
      statusCode: HttpStatus.INTERNAL_SERVER_ERROR,
      message: "Internal server error",
    });
  }
}
