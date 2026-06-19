import os
import sys
import logging
import argparse
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

DATAHUB_URL = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
DATAHUB_TOKEN = os.getenv("DATAHUB_TOKEN")
TAG_URN = "urn:li:tag:needs-owner"
PAGE_SIZE = 100


def graphql(query: str, variables: dict) -> dict:
    """Execute a GraphQL query against DataHub."""
    headers = {"Content-Type": "application/json"}

    if DATAHUB_TOKEN:
        headers["Authorization"] = f"Bearer {DATAHUB_TOKEN}"   

    response = requests.post(
        f"{DATAHUB_URL}/api/graphql",
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise Exception(f"GraphQL error: {data['errors']}")
    return data["data"]


def ensure_tag_exists():
    """Create the needs-owner tag if it doesn't exist yet."""
    mutation = """
    mutation createTag($input: CreateTagInput!) {
      createTag(input: $input)
    }
    """
    try:
        graphql(mutation, {"input": {"id": "needs-owner", "name": "needs-owner"}})
        log.info("Tag 'needs-owner' ensured.")
    except Exception as e:
        log.warning(f"Tag may already exist (safe to ignore): {e}")

def get_unowned_datasets() -> list:
    """Fetch all datasets, then filter for ones with no owners, handling pagination."""
    query = """
    query getDatasets($start: Int, $count: Int) {
      search(input: {
        type: DATASET,
        query: "*",
        start: $start,
        count: $count
      }) {
        total
        searchResults {
          entity {
            urn
            ... on Dataset {
              name
              ownership {
                owners {
                  owner {
                    ... on CorpUser { urn }
                    ... on CorpGroup { urn }
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    unowned = []
    start = 0
    total = None

    while True:
        data = graphql(query, {"start": start, "count": PAGE_SIZE})
        results = data["search"]["searchResults"]
        total = data["search"]["total"]

        for result in results:
            entity = result["entity"]
            ownership = entity.get("ownership")
            owners = ownership.get("owners", []) if ownership else []

            if not owners:
                unowned.append(entity["urn"])

        start += PAGE_SIZE
        if start >= total:
            break

    log.info(f"Found {len(unowned)} unowned datasets out of {total} total.")
    return unowned

def has_tag(urn: str) -> bool:
    """Check if a dataset already has the needs-owner tag."""
    query = """
    query getTags($urn: String!) {
      dataset(urn: $urn) {
        tags {
          tags {
            tag { urn }
          }
        }
      }
    }
    """
    data = graphql(query, {"urn": urn})
    dataset = data.get("dataset")

    if dataset is None:
        log.warning(f"Dataset not found when checking tags: {urn}")
        return False

    tags = dataset.get("tags")
    if tags is None:
        return False

    tag_list = tags.get("tags", [])
    return any(t["tag"]["urn"] == TAG_URN for t in tag_list)

def add_tag(urn: str):
    """Add the needs-owner tag to a dataset."""
    mutation = """
    mutation addTag($input: TagAssociationInput!) {
      addTag(input: $input)
    }
    """
    graphql(mutation, {
        "input": {
            "tagUrn": TAG_URN,
            "resourceUrn": urn
        }
    })


def run(dry_run: bool = False):
    log.info(f"Starting governance job. dry_run={dry_run}")
    ensure_tag_exists()

    unowned = get_unowned_datasets()

    if not unowned:
        log.info("No unowned datasets found. Nothing to do.")
        return

    tagged = 0
    skipped = 0
    failed = 0

    for urn in unowned:
        try:
            # Idempotency check — skip if already tagged
            if has_tag(urn):
                log.info(f"[SKIP] Already tagged: {urn}")
                skipped += 1
                continue

            if dry_run:
                log.info(f"[DRY-RUN] Would tag: {urn}")
                tagged += 1
            else:
                add_tag(urn)
                log.info(f"[TAGGED] {urn}")
                tagged += 1

        except Exception as e:
            log.error(f"[FAILED] {urn} — {e}")
            failed += 1

    log.info(
        f"Done. tagged={tagged}, skipped={skipped}, failed={failed}"
    )

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without making changes"
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run)