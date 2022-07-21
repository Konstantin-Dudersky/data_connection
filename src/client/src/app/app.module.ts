import { AppRoutingModule } from "./app-routing.module";
import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
// components ------------------------------------------------------------------
import { AppComponent } from "./app.component";
// primeng ---------------------------------------------------------------------

@NgModule({
    declarations: [AppComponent],
    imports: [
        BrowserModule,
        AppRoutingModule,
        // primeng -------------------------------------------------------------
        BrowserAnimationsModule,
    ],
    providers: [],
    bootstrap: [AppComponent],
})
export class AppModule {}
