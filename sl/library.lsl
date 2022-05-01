parse_response(body) {
    if (llGetSubString(value, 0, 0) == "1")
    {
        // the key-value pair was successfully read
        llSay(0, "New key-value pair value: " + llGetSubString(value, 2, -1));
    }
    else
    {
        // the key-value pair failed to read
        integer error =  (integer)llGetSubString(value, 2, -1);
        llSay(0, "Key-value failed to read: " + llGetExperienceErrorMessage(error));
    }    
}

default {
    dataserver(key t, string value) {
        if ( t == requestId ) {
            parse_response(value);
        }
    }
    
    http_response(key id, integer status, list metaData, string body)
    {
        if (id == requestId && status == 200)
        {
            parse_response(body);
        }
    }
}