from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class GitHubUserModel(BaseModel):
    """
    Represents a github user (public profile).
    Maps to the response from GET /user/{username} to GET /user

    BaseModel is pydantic's base class.
    All fields are declared as class attributes with typed annotations.
    Pydantic reads these and validates incoming data against them
    """

    # Required fileds - Github always sends these
    # If any are missing pydantic raises ValidationError immediately

    login: str
    id: int
    url: str
    html_url: str
    public_repos: int
    followers: int
    following: int
    created_at: datetime # Pydantic auto-converts "2023-07-06T14:34:11Z" ->datetime object

    #Optional fields - Github sends these but they can be None
    # Optional[str] means "str or None"
    # default=None means "if missing from response, use None - dont crash"
    name: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    location: Optional[str]= None
    email: Optional[str]=None
    bio: Optional[str]=None
    avatar_url: Optional[str]=None

    # Field with alias
    twitter_username: Optional[str] = Field(None, alias = "twitterUsername")
    account_type: Optional[str] = Field(None, alias= "type")

    # Model config tells python to behave:
    # Populate_by_name = True -> allow both field name and alias to work
    model_config={
        "populate_by_name": True,

        #extra="igmore" -> if the githib add new fields we didnt declare then slightly ignore those fields
        # apis add extra field sometimes
        "extra": "ignore"
    }

    # In Pydantic (specifically Pydantic v2), the @field_validator decorator allows you to write custom validation logic for individual fields on a model. 
    # It goes beyond basic type checking to let you enforce complex business rules, format incoming data, or catch errors before the object is created.
    # mode- 'after' (Default)Runs after Pydantic parses the type. (e.g., if input is "12", Pydantic converts it to 12 before your validator sees it).
    # mode- 'before'Runs before Pydantic does any parsing. You receive the raw, untrusted input data exactly as the user provided it.
    @field_validator("created_at", mode = "before")
    @classmethod
    def parse_datetime(cls, value):
        """
        Github send dates as ISO strings: "2023-07-06T14:34:11Z"
        Pydantic can parse this automatically, but this validator shows you
        how to write custom parsing logic when you need it.
        mode= "before" means this runs BEFORE pydantic's own type coercion.
        """
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    def display_name(self)-> str:
        """
        Helper method on model itself.
        Models can have method- they are just python classes
        """
        return self.name or self.login

class RepoOwnerModel(BaseModel):
    """
    Nested model - a repos owner is itself a user object.
    Github's repo repsponse contains an owner field which is a user dict.
    Pydantic handles nested models automatically.
    """
    login: str
    id: int
    html_url: str
    avatar_url: Optional[str]= None
    account_type: Optional[str] = Field(None, alias= "type")

    model_config= {"populate_by_name": True, "extra": "ignore"}

class RepoModel(BaseModel):
    """
    Represents GitHub Repository
    Maps to response from GET /repos/{owner}/{repo} or GET /user/repos
    """
    id: int
    name: str
    full_name: str
    html_url: str
    private: bool
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    default_branch: str
    created_at: datetime
    updated_at: datetime

    #Nested model- pydantic parses this dict into a RepoOwnerModelautomatically
    owner: RepoOwnerModel

    #Optional fields
    description: Optional[str] = None
    language: Optional[str] = None
    hoempage: Optional[str] = None
    size: Optional[int]= None
    watchers_count: Optional[int]= None
    pushed_at: Optional[datetime] = None

    model_config= {"extra": "ignore"}

    @field_validator("created_at", "updated_at", "pushed_at", mode= "before")
    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value,str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    def is_active(self, days: int = 90)-> bool:
        """
        Returns true of the repo was pushed to last N days.
        Example of useful business logic living on the model
        """ 
        if not self.pushed_at:
            return False
        
        from datetime import timezone
        now= datetime.now(timezone.utc)
        delta = now - self.pushed_at
        return delta.days <= days
    
    def summary(self) -> str:
        """One line summary of the repo"""
        status = "active" if self.is_active() else "inactive"
        return (
            f"name: {self.full_name} | "
            f"stagazers count: {self.stargazers_count} | "
            f"forks count: {self.forks_count} | "
            f"status: {status}"
        )


class RepoLanguagesModel(BaseModel):
    """
    Maps to GET /repos/{owner}/{repo}/languages
    Github returns: {"Python":12345, "JavaScript":6789}
    We wrap this in a model ato add helper methods.
    """

    # Languages is the raw dict from github
    languages: dict[str, int]

    @classmethod
    def from_response(cls, data: dict) -> RepoLanguagesModel:
        """
        Github returns the languages dict directly not nested.
        this factory method wraps it into our model structure.
        """
        return cls(languages=data)

    def total_bytes(self) -> int:
        return sum(self.languages.values())
    
    def primary_language(self) -> Optional[str]:
        """Returns the language with most bytes."""
        if not self.languages:
            return None
        return max(self.languages, key = self.languages.get)

    def percentages(self) -> dict[str, float]:
        """ Returns each language as percentage of total code"""
        total = self.total_bytes()
        if total == 0:
            return {}

        return {
            lang: round((bytes_/ total) *100,1)
            for lang, bytes_ in self.languages.items()
        }



        



    