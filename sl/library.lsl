string SECURE_HEADER_VALUE = "SOME_STRING";
string SLDB_URL = "Lambda URL with trailing slash";
key requestId = NULL_KEY;

readKeyValue( string data_key ) {
    string hash = llSHA1String(
        (string)llGetObjectKey() + data_key + SECURE_HEADER_VALUE
        );
    requestId = llHTTPRequest(
        SLDB_URL + data_key,
        [ HTTP_CUSTOM_HEADER, "secure", hash ],
        ""
    );
}

updateKeyValue( string data_key, string value ) {
    string hash = llSHA1String(
        (string)llGetObjectKey() + data_key + SECURE_HEADER_VALUE
        );
    requestId = llHTTPRequest(
        SLDB_URL + data_key,
        [ HTTP_METHOD, "PUT",
          HTTP_CUSTOM_HEADER, "Authentication", hash ],
        value
    );
}

parse_response(string body) {
    if (llGetSubString(body, 0, 0) == "1")
    {
        // the key-value pair was successfully read
        llSay(0, "New key-value pair value: " + llGetSubString(body, 2, -1));
    }
    else
    {
        // the key-value pair failed to read
        integer error =  (integer)llGetSubString(body, 2, -1);
        llSay(0, "Key-value failed to read: " + llGetExperienceErrorMessage(error));
    }    
}

default {
    touch_end(integer d) {
        readKeyValue( "test-key" )
    }

    http_response(key id, integer status, list metaData, string body)
    {
        if (id == requestId)
        {
            if ( status == 200 ) {
                parse_response(body);
            } else {
                llSay(0, "HTTP Error: " + (string)status + "\n" + body)
            }
            requestId = NULL_KEY
        }
    }
}
