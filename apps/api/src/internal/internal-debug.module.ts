import { Module } from "@nestjs/common";
import { InternalDebugShopConnectController } from "./internal-debug-shop-connect.controller";
import { ShopConnectDebugGuard } from "./shop-connect-debug.guard";

@Module({
  controllers: [InternalDebugShopConnectController],
  providers: [ShopConnectDebugGuard],
})
export class InternalDebugModule {}
