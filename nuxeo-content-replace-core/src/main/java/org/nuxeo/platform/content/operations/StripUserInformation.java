package org.nuxeo.platform.content.operations;

import java.io.IOException;
import java.io.Serializable;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang3.StringUtils;
import org.nuxeo.ecm.automation.core.Constants;
import org.nuxeo.ecm.automation.core.annotations.Context;
import org.nuxeo.ecm.automation.core.annotations.Operation;
import org.nuxeo.ecm.automation.core.annotations.OperationMethod;
import org.nuxeo.ecm.automation.core.annotations.Param;
import org.nuxeo.ecm.automation.core.collectors.BlobCollector;
import org.nuxeo.ecm.automation.core.collectors.DocumentModelCollector;
import org.nuxeo.ecm.automation.core.util.DocumentHelper;
import org.nuxeo.ecm.core.api.Blob;
import org.nuxeo.ecm.core.api.CoreSession;
import org.nuxeo.ecm.core.api.DocumentModel;
import org.nuxeo.ecm.core.api.blobholder.BlobHolder;
import org.nuxeo.ecm.core.api.blobholder.SimpleBlobHolder;
import org.nuxeo.ecm.core.convert.api.ConversionService;
import org.nuxeo.ecm.platform.mimetype.interfaces.MimetypeRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 *
 */
@Operation(id = StripUserInformation.ID, category = Constants.CAT_BLOB, label = "Strip Document User Information", description = "Remove the identifying user information from an office document.")
public class StripUserInformation {

    public static final String ID = "Blob.StripUserInformation";

    protected static final Logger LOG = LoggerFactory.getLogger(StripUserInformation.class);

    static final String CONVERTER = "stripUserInformation";

    @Context
    protected CoreSession session;

    @Context
    protected ConversionService service;

    @Context
    protected MimetypeRegistry mimeTypes;

    @Param(name = "xpath", required = false, description = "Blob path to use.", values = "file:content")
    protected String xpath = "file:content";

    @Param(name = "save", required = false, values = "true")
    protected boolean save = true;

    @OperationMethod(collector = DocumentModelCollector.class)
    public DocumentModel run(DocumentModel doc) throws IOException {
        Blob blob = (Blob) doc.getPropertyValue(xpath);
        if (blob == null) {
            BlobHolder bh = doc.getAdapter(BlobHolder.class);
            if (bh != null) {
                blob = bh.getBlob();
            }
        }

        Blob result = run(blob);
        DocumentHelper.addBlob(doc.getProperty(xpath), result);
        if (save) {
            doc = session.saveDocument(doc);
        }

        return doc;
    }

    @OperationMethod(collector = BlobCollector.class)
    public Blob run(Blob blob) throws IOException {
        if (blob != null) {
            blob = convert(new SimpleBlobHolder(blob)).getBlob();
        }
        return blob;
    }

    private BlobHolder convert(BlobHolder holder) throws IOException {

        String extension = null;

        // Get target type
        Blob blob = holder.getBlob();
        String file = blob.getFilename();
        if (StringUtils.isNotBlank(file)) {
            extension = FilenameUtils.getExtension(file);
        }
        if (StringUtils.isBlank(extension)) {
            List<String> exts = mimeTypes.getExtensionsFromMimetypeName(holder.getBlob().getMimeType());
            if (exts.size() > 0) {
                extension = exts.get(0);

            }
        }

        // Params for conversion
        Map<String, Serializable> params = new HashMap<>();
        params.put("type", extension);

        // Perform conversion
        BlobHolder result = service.convert("stripUserInformation", holder, params);
        Blob converted = result.getBlob();
        converted.setFilename(blob.getFilename());
        converted.setMimeType(blob.getMimeType());

        return result;
    }
}
