import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Optional;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Quick example showing how to fetch user settings from Garmin Connect API.
 *
 * Usage:
 *  - Set either ACCESS_TOKEN or COOKIE_STRING environment variable before running.
 *    ACCESS_TOKEN: a Bearer token (if you have one)
 *    COOKIE_STRING: raw cookie header from an authenticated browser session, e.g.
 *      "session-id=...; other-cookie=..."
 *
 *  Example:
 *    export ACCESS_TOKEN="eyJ..."; java -cp target/yourjar.jar GarminQuickExample
 */
public class GarminQuickExample {
    // Endpoint path shown in the python library
    private static final String USER_SETTINGS_PATH = "/userprofile-service/userprofile/user-settings";
    private static final String CONNECTAPI_HOST = "https://connectapi.garmin.com"; // or https://connectapi.garmin.cn for China
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static void main(String[] args) throws Exception {
        String accessToken = System.getenv("ACCESS_TOKEN"); // Bearer token
        String cookieString = System.getenv("COOKIE_STRING"); // raw cookie header

        if ((accessToken == null || accessToken.isBlank()) &&
            (cookieString == null || cookieString.isBlank())) {
            System.err.println("Please set ACCESS_TOKEN or COOKIE_STRING environment variable.");
            System.err.println("See comments in the source for how to obtain a token or cookie.");
            System.exit(1);
        }

        String url = CONNECTAPI_HOST + USER_SETTINGS_PATH;
        HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();

        HttpRequest.Builder reqBuilder = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(Duration.ofSeconds(20))
                .GET()
                .header("Accept", "application/json");

        // Prefer access token if available
        if (accessToken != null && !accessToken.isBlank()) {
            reqBuilder.header("Authorization", "Bearer " + accessToken);
            System.out.println("Using Authorization: Bearer <ACCESS_TOKEN>");
        } else {
            reqBuilder.header("Cookie", cookieString);
            System.out.println("Using Cookie header from COOKIE_STRING");
        }

        HttpRequest request = reqBuilder.build();

        System.out.println("Requesting: " + url);
        HttpResponse<String> resp = client.send(request, HttpResponse.BodyHandlers.ofString());

        int status = resp.statusCode();
        System.out.println("HTTP status: " + status);

        if (status == 200) {
            String body = resp.body();
            // Parse and pretty print
            try {
                JsonNode root = MAPPER.readTree(body);
                String pretty = MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(root);
                System.out.println("Response JSON:");
                System.out.println(pretty);
            } catch (IOException e) {
                System.out.println("Response (raw):");
                System.out.println(body);
            }
        } else if (status == 401) {
            System.err.println("Unauthorized (401). Token/session probably expired or invalid.");
            System.err.println("If you used a cookie, try copying the latest cookie from your browser.");
            System.err.println("If you used an access token, refresh it or use python-garminconnect to obtain a token.");
        } else {
            System.err.println("Non-OK response body:");
            System.err.println(resp.body());
        }
    }
}